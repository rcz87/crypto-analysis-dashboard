#!/usr/bin/env python3
"""
Audit Logger - Comprehensive audit logging untuk trading signals dan API calls
Secure logging dengan encryption dan tamper detection
"""

import logging
import time
import json
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import os
import sqlite3
from pathlib import Path
import threading
import queue

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    TRADING_SIGNAL = "trading_signal"
    API_CALL = "api_call"
    USER_LOGIN = "user_login"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"
    ERROR_EVENT = "error_event"

class AuditSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    timestamp: float
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: str
    user_agent: str
    endpoint: str
    method: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    execution_time_ms: float
    success: bool
    error_message: Optional[str]
    additional_context: Dict[str, Any]
    hash_signature: str

class AuditLogger:
    """
    Comprehensive audit logger dengan encryption dan tamper detection
    """
    
    def __init__(self, db_path: str = "logs/audit.db", secret_key: Optional[str] = None):
        self.db_path = db_path
        self.secret_key = secret_key or os.getenv('AUDIT_SECRET_KEY', 'default-audit-key-change-in-production')
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Background queue untuk async logging
        self.log_queue = queue.Queue()
        self.background_thread = threading.Thread(target=self._background_logger, daemon=True)
        self.background_thread.start()
        
        # Metrics tracking
        self.metrics = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'last_cleanup': time.time()
        }
        
        logger.info("📝 Audit Logger initialized with secure tamper detection")
    
    def _init_database(self):
        """Initialize SQLite database untuk audit logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create audit_events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        source_ip TEXT NOT NULL,
                        user_agent TEXT,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        request_data TEXT,
                        response_data TEXT,
                        execution_time_ms REAL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        additional_context TEXT,
                        hash_signature TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes untuk performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_ip ON audit_events(source_ip)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_endpoint ON audit_events(endpoint)')
                
                # Create audit_metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        total_events INTEGER NOT NULL,
                        events_by_type TEXT NOT NULL,
                        events_by_severity TEXT NOT NULL,
                        unique_users INTEGER NOT NULL,
                        unique_ips INTEGER NOT NULL,
                        error_rate REAL NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date)
                    )
                ''')
                
                conn.commit()
        
        except Exception as e:
            logger.error(f"Error initializing audit database: {e}")
    
    def _calculate_hash_signature(self, event_data: Dict[str, Any]) -> str:
        """Calculate HMAC signature untuk tamper detection"""
        # Create deterministic string dari event data
        data_string = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        
        # Calculate HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def log_event(self, 
                  event_type: AuditEventType,
                  severity: AuditSeverity,
                  endpoint: str,
                  method: str = "GET",
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  source_ip: str = "unknown",
                  user_agent: str = "",
                  request_data: Optional[Dict[str, Any]] = None,
                  response_data: Optional[Dict[str, Any]] = None,
                  execution_time_ms: float = 0.0,
                  success: bool = True,
                  error_message: Optional[str] = None,
                  additional_context: Optional[Dict[str, Any]] = None):
        """
        Log audit event (async via queue)
        """
        try:
            # Prepare event data
            event_data = {
                'timestamp': time.time(),
                'event_type': event_type.value,
                'severity': severity.value,
                'user_id': user_id,
                'session_id': session_id,
                'source_ip': source_ip,
                'user_agent': user_agent,
                'endpoint': endpoint,
                'method': method,
                'request_data': request_data or {},
                'response_data': response_data or {},
                'execution_time_ms': execution_time_ms,
                'success': success,
                'error_message': error_message,
                'additional_context': additional_context or {}
            }
            
            # Calculate hash signature
            hash_signature = self._calculate_hash_signature(event_data)
            event_data['hash_signature'] = hash_signature
            
            # Create audit event object
            event = AuditEvent(**event_data)
            
            # Add to queue untuk background processing
            self.log_queue.put(event)
            
            # Update metrics
            self.metrics['total_events'] += 1
            self.metrics['events_by_type'][event_type.value] = self.metrics['events_by_type'].get(event_type.value, 0) + 1
            self.metrics['events_by_severity'][severity.value] = self.metrics['events_by_severity'].get(severity.value, 0) + 1
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    def _background_logger(self):
        """Background thread untuk processing audit events"""
        while True:
            try:
                # Get event dari queue (blocking)
                event = self.log_queue.get(timeout=1)
                
                # Store dalam database
                self._store_event_to_db(event)
                
                # Mark task sebagai done
                self.log_queue.task_done()
                
            except queue.Empty:
                # Perform periodic cleanup
                current_time = time.time()
                if current_time - self.metrics['last_cleanup'] > 3600:  # Every hour
                    self._cleanup_old_events()
                    self.metrics['last_cleanup'] = current_time
                
            except Exception as e:
                logger.error(f"Error in background audit logger: {e}")
    
    def _store_event_to_db(self, event: AuditEvent):
        """Store audit event ke database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO audit_events (
                        timestamp, event_type, severity, user_id, session_id,
                        source_ip, user_agent, endpoint, method, request_data,
                        response_data, execution_time_ms, success, error_message,
                        additional_context, hash_signature
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.timestamp,
                    event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type),
                    event.severity.value if hasattr(event.severity, 'value') else str(event.severity),
                    event.user_id,
                    event.session_id,
                    event.source_ip,
                    event.user_agent,
                    event.endpoint,
                    event.method,
                    json.dumps(event.request_data),
                    json.dumps(event.response_data),
                    event.execution_time_ms,
                    event.success,
                    event.error_message,
                    json.dumps(event.additional_context),
                    event.hash_signature
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing audit event to database: {e}")
    
    def _cleanup_old_events(self, days_to_keep: int = 90):
        """Cleanup old audit events"""
        try:
            cutoff_timestamp = time.time() - (days_to_keep * 86400)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old events
                cursor.execute('DELETE FROM audit_events WHERE timestamp < ?', (cutoff_timestamp,))
                deleted_count = cursor.rowcount
                
                # Vacuum database
                cursor.execute('VACUUM')
                
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old audit events")
                
        except Exception as e:
            logger.error(f"Error cleaning up old audit events: {e}")
    
    def get_events(self, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   event_type: Optional[AuditEventType] = None,
                   user_id: Optional[str] = None,
                   source_ip: Optional[str] = None,
                   endpoint: Optional[str] = None,
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve audit events dengan filtering
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query
                where_conditions = []
                params = []
                
                if start_time:
                    where_conditions.append('timestamp >= ?')
                    params.append(start_time)
                
                if end_time:
                    where_conditions.append('timestamp <= ?')
                    params.append(end_time)
                
                if event_type:
                    where_conditions.append('event_type = ?')
                    params.append(event_type.value)
                
                if user_id:
                    where_conditions.append('user_id = ?')
                    params.append(user_id)
                
                if source_ip:
                    where_conditions.append('source_ip = ?')
                    params.append(source_ip)
                
                if endpoint:
                    where_conditions.append('endpoint LIKE ?')
                    params.append(f'%{endpoint}%')
                
                where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
                
                query = f'''
                    SELECT * FROM audit_events 
                    WHERE {where_clause}
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                params.append(limit)
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                
                events = []
                for row in cursor.fetchall():
                    event_dict = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    try:
                        event_dict['request_data'] = json.loads(event_dict['request_data'] or '{}')
                        event_dict['response_data'] = json.loads(event_dict['response_data'] or '{}')
                        event_dict['additional_context'] = json.loads(event_dict['additional_context'] or '{}')
                    except json.JSONDecodeError:
                        pass
                    
                    events.append(event_dict)
                
                return events
                
        except Exception as e:
            logger.error(f"Error retrieving audit events: {e}")
            return []
    
    def verify_event_integrity(self, event_id: int) -> Tuple[bool, str]:
        """
        Verify integrity audit event using hash signature
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM audit_events WHERE id = ?', (event_id,))
                row = cursor.fetchone()
                
                if not row:
                    return False, "Event not found"
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                event_data = dict(zip(columns, row))
                
                # Extract stored signature
                stored_signature = event_data.pop('hash_signature')
                event_data.pop('id')  # Remove auto-generated ID
                event_data.pop('created_at')  # Remove auto-generated timestamp
                
                # Parse JSON fields
                try:
                    event_data['request_data'] = json.loads(event_data['request_data'] or '{}')
                    event_data['response_data'] = json.loads(event_data['response_data'] or '{}')
                    event_data['additional_context'] = json.loads(event_data['additional_context'] or '{}')
                except json.JSONDecodeError:
                    pass
                
                # Calculate signature
                calculated_signature = self._calculate_hash_signature(event_data)
                
                if calculated_signature == stored_signature:
                    return True, "Event integrity verified"
                else:
                    return False, "Event integrity compromised - hash mismatch"
                
        except Exception as e:
            logger.error(f"Error verifying event integrity: {e}")
            return False, f"Verification error: {str(e)}"
    
    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get audit summary untuk dashboard
        """
        try:
            start_time = time.time() - (days * 86400)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total events
                cursor.execute('SELECT COUNT(*) FROM audit_events WHERE timestamp >= ?', (start_time,))
                total_events = cursor.fetchone()[0]
                
                # Events by type
                cursor.execute('''
                    SELECT event_type, COUNT(*) 
                    FROM audit_events 
                    WHERE timestamp >= ? 
                    GROUP BY event_type
                ''', (start_time,))
                events_by_type = dict(cursor.fetchall())
                
                # Events by severity
                cursor.execute('''
                    SELECT severity, COUNT(*) 
                    FROM audit_events 
                    WHERE timestamp >= ? 
                    GROUP BY severity
                ''', (start_time,))
                events_by_severity = dict(cursor.fetchall())
                
                # Error rate
                cursor.execute('SELECT COUNT(*) FROM audit_events WHERE timestamp >= ? AND success = 0', (start_time,))
                error_count = cursor.fetchone()[0]
                error_rate = (error_count / max(1, total_events)) * 100
                
                # Unique users
                cursor.execute('SELECT COUNT(DISTINCT user_id) FROM audit_events WHERE timestamp >= ? AND user_id IS NOT NULL', (start_time,))
                unique_users = cursor.fetchone()[0]
                
                # Unique IPs
                cursor.execute('SELECT COUNT(DISTINCT source_ip) FROM audit_events WHERE timestamp >= ?', (start_time,))
                unique_ips = cursor.fetchone()[0]
                
                # Top endpoints
                cursor.execute('''
                    SELECT endpoint, COUNT(*) as count 
                    FROM audit_events 
                    WHERE timestamp >= ? 
                    GROUP BY endpoint 
                    ORDER BY count DESC 
                    LIMIT 10
                ''', (start_time,))
                top_endpoints = cursor.fetchall()
                
                # Recent critical events
                cursor.execute('''
                    SELECT timestamp, event_type, endpoint, error_message 
                    FROM audit_events 
                    WHERE timestamp >= ? AND severity = 'critical' 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''', (start_time,))
                critical_events = cursor.fetchall()
                
                return {
                    'period_days': days,
                    'total_events': total_events,
                    'events_by_type': events_by_type,
                    'events_by_severity': events_by_severity,
                    'error_rate_percentage': round(error_rate, 2),
                    'unique_users': unique_users,
                    'unique_ips': unique_ips,
                    'top_endpoints': [{'endpoint': ep, 'count': count} for ep, count in top_endpoints],
                    'recent_critical_events': [
                        {
                            'timestamp': ts,
                            'type': event_type,
                            'endpoint': endpoint,
                            'error': error_msg
                        } for ts, event_type, endpoint, error_msg in critical_events
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error generating audit summary: {e}")
            return {'error': str(e)}
    
    def log_trading_signal(self, 
                          signal_data: Dict[str, Any],
                          user_id: Optional[str] = None,
                          source_ip: str = "system",
                          execution_time_ms: float = 0.0,
                          success: bool = True,
                          error_message: Optional[str] = None):
        """
        Log trading signal generation
        """
        self.log_event(
            event_type=AuditEventType.TRADING_SIGNAL,
            severity=AuditSeverity.INFO if success else AuditSeverity.ERROR,
            endpoint='/trading/signal',
            method='POST',
            user_id=user_id,
            source_ip=source_ip,
            request_data={'signal_type': signal_data.get('signal_type', 'unknown')},
            response_data=signal_data,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            additional_context={'signal_id': signal_data.get('id', 'unknown')}
        )
    
    def log_api_call(self,
                    endpoint: str,
                    method: str,
                    user_id: Optional[str] = None,
                    source_ip: str = "unknown",
                    user_agent: str = "",
                    request_data: Optional[Dict[str, Any]] = None,
                    response_data: Optional[Dict[str, Any]] = None,
                    execution_time_ms: float = 0.0,
                    success: bool = True,
                    error_message: Optional[str] = None):
        """
        Log API call
        """
        severity = AuditSeverity.INFO
        if not success:
            severity = AuditSeverity.ERROR
        elif execution_time_ms > 5000:  # Slow response
            severity = AuditSeverity.WARNING
        
        self.log_event(
            event_type=AuditEventType.API_CALL,
            severity=severity,
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            request_data=request_data,
            response_data=response_data,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message
        )

# Global instance
audit_logger = AuditLogger()

def get_audit_logger():
    """Get global audit logger instance"""
    return audit_logger

logger.info("📝 Audit Logger module initialized")