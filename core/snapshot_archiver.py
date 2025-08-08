#!/usr/bin/env python3
"""
Snapshot Archiver System
Handles snapshot storage, retrieval, and management with PDF report generation
"""

import os
import json
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("ReportLab not available - PDF generation disabled")

# Local imports
# Import models locally to avoid circular imports
from core.snapshot_generator import MarketSnapshot, SnapshotType

logger = logging.getLogger(__name__)

class SnapshotArchiver:
    """Advanced snapshot archiver with PDF report generation and data management"""
    
    def __init__(self):
        self.archive_path = Path("snapshots")
        self.archive_path.mkdir(exist_ok=True)
        
        # PDF configuration
        self.pdf_path = self.archive_path / "reports"
        self.pdf_path.mkdir(exist_ok=True)
        
        # Configuration
        self.max_snapshots_per_symbol = 100
        self.cleanup_older_than_days = 30
        
        logger.info("SnapshotArchiver initialized")
    
    def get_snapshots(self, symbol: str = None, timeframe: str = None, 
                     session_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve snapshots from database
        
        Args:
            symbol: Filter by symbol
            timeframe: Filter by timeframe
            session_id: Filter by session
            limit: Maximum number of snapshots to return
            
        Returns:
            List of snapshot dictionaries
        """
        try:
            from app import db
            from models import AISnapshotArchive
            
            # Build query
            query = AISnapshotArchive.query
            
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            if timeframe:
                query = query.filter_by(timeframe=timeframe)
            if session_id:
                query = query.filter_by(session_id=session_id)
            
            # Order by creation time and limit
            query = query.order_by(AISnapshotArchive.created_at.desc()).limit(limit)
            
            snapshots = query.all()
            
            return [snapshot.to_dict() for snapshot in snapshots]
            
        except Exception as e:
            logger.error(f"Error retrieving snapshots: {e}")
            return []
    
    def get_snapshot_by_id(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        """Get specific snapshot by ID"""
        try:
            from app import db
            from models import AISnapshotArchive
            
            snapshot = AISnapshotArchive.query.get(snapshot_id)
            if snapshot:
                return snapshot.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving snapshot {snapshot_id}: {e}")
            return None
    
    def get_snapshot_statistics(self, symbol: str = None, 
                               timeframe: str = None) -> Dict[str, Any]:
        """Get snapshot statistics"""
        try:
            from app import db
            
            # Build base query
            query = AISnapshotArchive.query
            
            if symbol:
                query = query.filter_by(symbol=symbol.upper())
            if timeframe:
                query = query.filter_by(timeframe=timeframe)
            
            # Get counts
            total_snapshots = query.count()
            
            # Get snapshots from last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_snapshots = query.filter(AISnapshotArchive.created_at >= yesterday).count()
            
            # Get average confidence
            avg_confidence = query.with_entities(
                db.func.avg(AISnapshotArchive.confidence)
            ).scalar() or 0.0
            
            # Get symbol distribution
            symbol_stats = db.session.query(
                AISnapshotArchive.symbol,
                db.func.count(AISnapshotArchive.id).label('count')
            ).group_by(AISnapshotArchive.symbol).all()
            
            return {
                'total_snapshots': total_snapshots,
                'recent_snapshots': recent_snapshots,
                'average_confidence': float(avg_confidence),
                'symbol_distribution': {symbol: count for symbol, count in symbol_stats},
                'statistics_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting snapshot statistics: {e}")
            return {}
    
    def delete_snapshot(self, snapshot_id: int) -> bool:
        """Delete specific snapshot"""
        try:
            from app import db
            
            snapshot = AISnapshotArchive.query.get(snapshot_id)
            if snapshot:
                db.session.delete(snapshot)
                db.session.commit()
                logger.info(f"Snapshot {snapshot_id} deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting snapshot {snapshot_id}: {e}")
            return False
    
    def cleanup_old_snapshots(self, days: int = None) -> int:
        """Clean up old snapshots"""
        try:
            from app import db
            
            days = days or self.cleanup_older_than_days
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old snapshots
            deleted_count = AISnapshotArchive.query.filter(
                AISnapshotArchive.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old snapshots")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old snapshots: {e}")
            return 0
    
    def export_snapshots_to_json(self, symbol: str = None, 
                                timeframe: str = None, 
                                filename: str = None) -> str:
        """Export snapshots to JSON file"""
        try:
            snapshots = self.get_snapshots(symbol=symbol, timeframe=timeframe, limit=1000)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshots_{symbol or 'all'}_{timestamp}.json"
            
            filepath = self.archive_path / filename
            
            with open(filepath, 'w') as f:
                json.dump(snapshots, f, indent=2, default=str)
            
            logger.info(f"Exported {len(snapshots)} snapshots to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting snapshots: {e}")
            return ""
    
    def generate_pdf_report(self, symbol: str, timeframe: str = '1H', 
                           snapshot_id: int = None) -> str:
        """Generate PDF report for snapshot analysis"""
        if not PDF_AVAILABLE:
            logger.error("PDF generation not available - reportlab not installed")
            return ""
        
        try:
            # Get snapshot data
            if snapshot_id:
                snapshot_data = self.get_snapshot_by_id(snapshot_id)
                if not snapshot_data:
                    raise ValueError(f"Snapshot {snapshot_id} not found")
            else:
                # Get latest snapshot
                snapshots = self.get_snapshots(symbol=symbol, timeframe=timeframe, limit=1)
                if not snapshots:
                    raise ValueError(f"No snapshots found for {symbol}")
                snapshot_data = snapshots[0]
            
            # Create PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"report_{symbol}_{timestamp}.pdf"
            pdf_filepath = self.pdf_path / pdf_filename
            
            doc = SimpleDocTemplate(str(pdf_filepath), pagesize=A4)
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            # Title
            title = Paragraph(f"Market Analysis Report - {symbol}", title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Snapshot metadata
            snapshot_info = [
                ['Symbol', symbol],
                ['Timeframe', timeframe],
                ['Generated', snapshot_data.get('created_at', 'N/A')],
                ['Confidence', f"{snapshot_data.get('confidence', 0) * 100:.1f}%"],
                ['Current Price', f"${snapshot_data.get('snapshot_data', {}).get('current_price', 0):,.2f}"],
                ['24h Change', f"{snapshot_data.get('snapshot_data', {}).get('price_change_24h', 0):+.2f}%"]
            ]
            
            info_table = Table(snapshot_info, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Technical indicators
            story.append(Paragraph("Technical Indicators", styles['Heading2']))
            
            snapshot_main_data = snapshot_data.get('snapshot_data', {})
            
            tech_indicators = [
                ['Indicator', 'Value', 'Status'],
                ['RSI', f"{snapshot_main_data.get('rsi', 0):.1f}", 
                 'Overbought' if snapshot_main_data.get('rsi', 0) > 70 else 'Oversold' if snapshot_main_data.get('rsi', 0) < 30 else 'Normal'],
                ['EMA 20', f"${snapshot_main_data.get('ema_20', 0):,.2f}", 
                 'Bullish' if snapshot_main_data.get('current_price', 0) > snapshot_main_data.get('ema_20', 0) else 'Bearish'],
                ['EMA 50', f"${snapshot_main_data.get('ema_50', 0):,.2f}", 
                 'Bullish' if snapshot_main_data.get('current_price', 0) > snapshot_main_data.get('ema_50', 0) else 'Bearish'],
                ['MACD', f"{snapshot_main_data.get('macd', {}).get('macd', 0):.4f}", 
                 'Bullish' if snapshot_main_data.get('macd', {}).get('macd', 0) > 0 else 'Bearish']
            ]
            
            tech_table = Table(tech_indicators, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(tech_table)
            story.append(Spacer(1, 20))
            
            # AI Narrative
            story.append(Paragraph("AI Analysis", styles['Heading2']))
            ai_narrative = snapshot_data.get('ai_narrative', 'No AI analysis available')
            
            # Split narrative into paragraphs
            narrative_paragraphs = ai_narrative.split('\n\n')
            for para in narrative_paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 20))
            
            # Risk Assessment
            story.append(Paragraph("Risk Assessment", styles['Heading2']))
            risk_data = snapshot_main_data.get('risk_assessment', {})
            
            risk_info = [
                ['Risk Level', risk_data.get('risk_level', 'MEDIUM')],
                ['Risk Score', f"{risk_data.get('risk_score', 50)}/100"],
                ['Volatility', risk_data.get('volatility', 'MEDIUM')],
                ['Recommendation', 'Proceed with caution' if risk_data.get('risk_level') == 'HIGH' else 'Moderate risk']
            ]
            
            risk_table = Table(risk_info, colWidths=[2*inch, 3*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red if risk_data.get('risk_level') == 'HIGH' else colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(risk_table)
            story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph("Generated by Advanced Trading System", styles['Normal']))
            story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated: {pdf_filepath}")
            return str(pdf_filepath)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return ""
    
    def get_comparative_analysis(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Get comparative analysis over time"""
        try:
            from app import db
            
            # Get snapshots from last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            snapshots = AISnapshotArchive.query.filter(
                AISnapshotArchive.symbol == symbol.upper(),
                AISnapshotArchive.created_at >= start_date
            ).order_by(AISnapshotArchive.created_at.asc()).all()
            
            if not snapshots:
                return {}
            
            # Extract key metrics over time
            time_series = []
            for snapshot in snapshots:
                snapshot_data = snapshot.snapshot_data or {}
                time_series.append({
                    'timestamp': snapshot.created_at.isoformat(),
                    'price': snapshot_data.get('current_price', 0),
                    'rsi': snapshot_data.get('rsi', 0),
                    'confidence': snapshot.confidence or 0,
                    'volume': snapshot_data.get('volume_24h', 0)
                })
            
            # Calculate trends
            prices = [point['price'] for point in time_series if point['price'] > 0]
            rsi_values = [point['rsi'] for point in time_series if point['rsi'] > 0]
            
            price_trend = 'BULLISH' if prices[-1] > prices[0] else 'BEARISH' if prices else 'NEUTRAL'
            avg_rsi = sum(rsi_values) / len(rsi_values) if rsi_values else 50
            
            return {
                'symbol': symbol,
                'period_days': days,
                'snapshot_count': len(snapshots),
                'price_trend': price_trend,
                'price_change_percent': ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 1 else 0,
                'average_rsi': avg_rsi,
                'time_series': time_series,
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comparative analysis: {e}")
            return {}

def create_snapshot_archiver() -> SnapshotArchiver:
    """Factory function to create snapshot archiver"""
    return SnapshotArchiver()

# Global instance
snapshot_archiver = create_snapshot_archiver()