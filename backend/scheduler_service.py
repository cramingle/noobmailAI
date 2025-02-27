from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from models import NewsletterSchedule, engine
from email_service import send_email
import logging

logger = logging.getLogger(__name__)
Session = sessionmaker(bind=engine)

class NewsletterSchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        
    async def schedule_newsletter(self, name: str, description: str, template_content: str,
                                recipient_group: str, frequency: str, start_date: datetime):
        """Schedule a new recurring newsletter"""
        session = Session()
        try:
            # Create new schedule
            schedule = NewsletterSchedule(
                name=name,
                description=description,
                template_content=template_content,
                recipient_group=recipient_group,
                frequency=frequency,
                next_send_date=start_date
            )
            session.add(schedule)
            session.commit()
            
            # Add job to scheduler
            self._add_newsletter_job(schedule)
            
            return {"status": "success", "message": f"Newsletter '{name}' scheduled successfully"}
        except Exception as e:
            logger.error(f"Error scheduling newsletter: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def _add_newsletter_job(self, schedule: NewsletterSchedule):
        """Add a newsletter job to the scheduler"""
        job_id = f"newsletter_{schedule.id}"
        
        # Convert frequency to cron expression
        if schedule.frequency == "monthly":
            # Run on the same day of month as start_date
            day = schedule.next_send_date.day
            trigger = CronTrigger(day=day)
        elif schedule.frequency == "weekly":
            # Run on the same day of week as start_date
            day_of_week = schedule.next_send_date.strftime("%a").lower()
            trigger = CronTrigger(day_of_week=day_of_week)
        else:
            raise ValueError(f"Unsupported frequency: {schedule.frequency}")
        
        self.scheduler.add_job(
            self._send_newsletter,
            trigger=trigger,
            args=[schedule.id],
            id=job_id,
            replace_existing=True
        )
    
    async def _send_newsletter(self, schedule_id: int):
        """Send a scheduled newsletter"""
        session = Session()
        try:
            schedule = session.query(NewsletterSchedule).get(schedule_id)
            if not schedule or not schedule.is_active:
                return
            
            # Send the newsletter
            result = send_email(
                content=schedule.template_content,
                recipients=self._get_recipients(schedule.recipient_group),
                smtp_config=self._get_smtp_config(),
                campaign_name=schedule.name
            )
            
            # Update schedule
            schedule.last_sent_date = datetime.utcnow()
            if schedule.frequency == "monthly":
                schedule.next_send_date = schedule.next_send_date + timedelta(days=30)
            elif schedule.frequency == "weekly":
                schedule.next_send_date = schedule.next_send_date + timedelta(days=7)
            
            session.commit()
            
            logger.info(f"Newsletter '{schedule.name}' sent successfully")
            return result
        except Exception as e:
            logger.error(f"Error sending newsletter: {str(e)}")
            raise
        finally:
            session.close()
    
    def _get_recipients(self, group_name: str) -> list:
        """Get recipients for a group"""
        # TODO: Implement recipient group lookup
        return []
    
    def _get_smtp_config(self) -> dict:
        """Get SMTP configuration"""
        # TODO: Implement SMTP config lookup
        return {} 