"""
Утилиты для работы с базой данных.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, sessionmaker
from sqlalchemy import select, text
from config import DATABASE_URL
from models import (
    UserModel, CompetitionModel, RegistrationModel, RegistrationStatus,
    TimeSlotModel, VoterTimeSlotModel, JuryPanelModel, VoterJuryPanelModel, Base
)
from migrations.migration_manager import MigrationManager


class DatabaseManager:
    """Класс для управления подключением к БД."""

    def __init__(self) -> None:
        """Инициализация менеджера БД."""
        self.engine: Optional[AsyncEngine] = None
        self.async_session_maker: Optional[sessionmaker] = None

    async def init_db(self) -> None:
        """Инициализировать БД и создать таблицы."""
        # Create tables using synchronous engine first
        import sqlalchemy
        sync_url = DATABASE_URL.replace('sqlite+aiosqlite:', 'sqlite:')
        sync_engine = sqlalchemy.create_engine(sync_url, echo=False)
        Base.metadata.create_all(sync_engine)
        sync_engine.dispose()

        # Then create async engine
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.async_session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        # Run migrations
        migration_manager = MigrationManager(self.engine, self.async_session_maker)
        await migration_manager.run_migrations()

    async def close_db(self) -> None:
        """Закрыть подключение к БД."""
        if self.engine:
            await self.engine.dispose()

    def get_session(self) -> AsyncSession:
        """Получить сессию БД."""
        return self.async_session_maker()

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserModel]:
        """Получить пользователя по telegram_id."""
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserModel).where(UserModel.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, telegram_username: str, **kwargs: Any) -> UserModel:
        """Создать нового пользователя."""
        async with self.get_session() as session:
            user: UserModel = UserModel(
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                **kwargs
            )
            session.add(user)
            await session.commit()
            return user

    async def update_user(self, telegram_id: int, **kwargs: Any) -> Optional[UserModel]:
        """Обновить данные пользователя."""
        user: Optional[UserModel] = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None

        async with self.get_session() as session:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.add(user)
            await session.commit()
            return user

    async def get_active_competitions(self) -> List[Dict[str, Any]]:
        """Получить список активных соревнований."""
        async with self.get_session() as session:
            from sqlalchemy import select
            from .serializers import CompetitionSerializer
            result = await session.execute(
                select(CompetitionModel).where(CompetitionModel.is_active == True)
            )
            competitions = result.scalars().all()
            return CompetitionSerializer.serialize_list(competitions)

    async def get_competition_by_id(self, competition_id: int) -> CompetitionModel:
        """Получить соревнование по ID."""
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(CompetitionModel).where(CompetitionModel.id == competition_id)
            )
            return result.scalar_one_or_none()

    async def create_registration(
        self, user_id: int, telegram_id: int, competition_id: int, role: str,
        status: str = RegistrationStatus.PENDING.value
    ) -> RegistrationModel:
        """Создать регистрацию пользователя на соревнование."""
        async with self.get_session() as session:
            registration = RegistrationModel(
                user_id=user_id,
                telegram_id=telegram_id,
                competition_id=competition_id,
                role=role,
                status=status,
                is_confirmed=(status == RegistrationStatus.APPROVED.value),
            )
            session.add(registration)
            await session.commit()
            return registration

    async def phone_exists(self, phone: str) -> bool:
        """Проверить, существует ли пользователь с таким телефоном."""
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserModel).where(UserModel.phone == phone)
            )
            return result.scalar_one_or_none() is not None

    async def email_exists(self, email: str) -> bool:
        """Проверить, существует ли пользователь с таким email."""
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            return result.scalar_one_or_none() is not None

    # ===== REGISTRATION APPROVAL METHODS =====

    async def get_pending_registrations(self, competition_id=None, role=None) -> list:
        """Получить заявки со статусом pending."""
        async with self.get_session() as session:
            query = select(RegistrationModel).where(
                RegistrationModel.status == RegistrationStatus.PENDING.value
            )

            if competition_id:
                query = query.where(RegistrationModel.competition_id == competition_id)
            if role:
                query = query.where(RegistrationModel.role == role)

            result = await session.execute(query)
            return result.scalars().all()

    async def get_registrations_by_status(self, status: str) -> list:
        """Получить все регистрации по статусу."""
        async with self.get_session() as session:
            result = await session.execute(
                select(RegistrationModel).where(RegistrationModel.status == status)
            )
            return result.scalars().all()

    async def approve_registration(self, registration_id: int, admin_telegram_id: int) -> RegistrationModel:
        """Одобрить заявку."""
        async with self.get_session() as session:
            registration = await session.get(RegistrationModel, registration_id)
            if registration:
                from datetime import datetime
                registration.status = RegistrationStatus.APPROVED.value
                registration.is_confirmed = True
                registration.confirmed_at = datetime.utcnow()
                registration.confirmed_by = admin_telegram_id
                session.add(registration)
                await session.commit()
            return registration

    async def reject_registration(self, registration_id: int) -> RegistrationModel:
        """Отклонить заявку."""
        async with self.get_session() as session:
            registration = await session.get(RegistrationModel, registration_id)
            if registration:
                registration.status = RegistrationStatus.REJECTED.value
                registration.is_confirmed = False
                session.add(registration)
                await session.commit()
            return registration

    async def revoke_registration(self, registration_id: int) -> RegistrationModel:
        """Отозвать ранее одобренную заявку."""
        async with self.get_session() as session:
            registration = await session.get(RegistrationModel, registration_id)
            if registration:
                registration.status = RegistrationStatus.PENDING.value
                registration.is_confirmed = False
                registration.confirmed_at = None
                registration.confirmed_by = None
                session.add(registration)
                await session.commit()
            return registration

    async def get_registration_with_user(self, registration_id: int) -> dict:
        """Получить регистрацию с данными пользователя (JOIN)."""
        async with self.get_session() as session:
            registration = await session.get(RegistrationModel, registration_id)
            if not registration:
                return None

            user = await session.get(UserModel, registration.user_id)
            competition = await session.get(CompetitionModel, registration.competition_id)

            return {
                "registration_id": registration.id,
                "user_id": registration.user_id,
                "telegram_id": registration.telegram_id,
                "competition_id": registration.competition_id,
                "role": registration.role,
                "status": registration.status,
                "confirmed_at": registration.confirmed_at,
                "confirmed_by": registration.confirmed_by,
                "first_name": user.first_name if user else None,
                "last_name": user.last_name if user else None,
                "email": user.email if user else None,
                "phone": user.phone if user else None,
                "telegram_username": user.telegram_username if user else None,
                "bio": user.bio if user else None,
                "competition_name": competition.name if competition else None,
            }

    # ===== TIME SLOT METHODS =====

    async def get_time_slots_for_competition(self, competition_id: int) -> list:
        """Получить все временные слоты для соревнования."""
        async with self.get_session() as session:
            result = await session.execute(
                select(TimeSlotModel).where(
                    TimeSlotModel.competition_id == competition_id
                ).order_by(TimeSlotModel.slot_day, TimeSlotModel.start_time)
            )
            return result.scalars().all()

    async def create_time_slot(
        self, competition_id: int, slot_day, start_time, end_time, max_voters: int = 10
    ) -> TimeSlotModel:
        """Создать временной слот."""
        async with self.get_session() as session:
            time_slot = TimeSlotModel(
                competition_id=competition_id,
                slot_day=slot_day,
                start_time=start_time,
                end_time=end_time,
                max_voters=max_voters,
            )
            session.add(time_slot)
            await session.commit()
            return time_slot

    async def get_available_time_slots(self, competition_id: int) -> list:
        """Получить слоты с доступными местами."""
        async with self.get_session() as session:
            time_slots = await self.get_time_slots_for_competition(competition_id)
            available = []

            for slot in time_slots:
                # Count voters already assigned
                result = await session.execute(
                    select(VoterTimeSlotModel).where(
                        VoterTimeSlotModel.time_slot_id == slot.id
                    )
                )
                assigned_count = len(result.scalars().all())

                if assigned_count < slot.max_voters and slot.is_active:
                    available.append({
                        "slot": slot,
                        "assigned": assigned_count,
                        "available": slot.max_voters - assigned_count,
                    })

            return available

    async def assign_voter_to_time_slot(self, registration_id: int, time_slot_id: int) -> VoterTimeSlotModel:
        """Назначить voter на временной слот."""
        async with self.get_session() as session:
            voter_slot = VoterTimeSlotModel(
                registration_id=registration_id,
                time_slot_id=time_slot_id,
            )
            session.add(voter_slot)
            await session.commit()
            return voter_slot

    async def get_voter_time_slots(self, registration_id: int) -> list:
        """Получить выбранные слоты voter'а."""
        async with self.get_session() as session:
            result = await session.execute(
                select(VoterTimeSlotModel).where(
                    VoterTimeSlotModel.registration_id == registration_id
                )
            )
            voter_slots = result.scalars().all()

            time_slots = []
            for vs in voter_slots:
                time_slot = await session.get(TimeSlotModel, vs.time_slot_id)
                if time_slot:
                    time_slots.append(time_slot)

            return time_slots

    # ===== JURY PANEL METHODS =====

    async def get_jury_panels_for_competition(self, competition_id: int) -> list:
        """Получить судейские коллегии."""
        async with self.get_session() as session:
            result = await session.execute(
                select(JuryPanelModel).where(
                    JuryPanelModel.competition_id == competition_id
                )
            )
            return result.scalars().all()

    async def create_jury_panel(
        self, competition_id: int, panel_name: str, max_voters: int = 5
    ) -> JuryPanelModel:
        """Создать судейскую коллегию."""
        async with self.get_session() as session:
            jury_panel = JuryPanelModel(
                competition_id=competition_id,
                panel_name=panel_name,
                max_voters=max_voters,
            )
            session.add(jury_panel)
            await session.commit()
            return jury_panel

    async def assign_voter_to_jury_panel(self, registration_id: int, jury_panel_id: int) -> VoterJuryPanelModel:
        """Назначить voter в судейскую коллегию."""
        async with self.get_session() as session:
            voter_panel = VoterJuryPanelModel(
                registration_id=registration_id,
                jury_panel_id=jury_panel_id,
            )
            session.add(voter_panel)
            await session.commit()
            return voter_panel

    async def get_voter_jury_panels(self, registration_id: int) -> list:
        """Получить судейские коллегии voter'а."""
        async with self.get_session() as session:
            result = await session.execute(
                select(VoterJuryPanelModel).where(
                    VoterJuryPanelModel.registration_id == registration_id
                )
            )
            voter_panels = result.scalars().all()

            jury_panels = []
            for vp in voter_panels:
                jury_panel = await session.get(JuryPanelModel, vp.jury_panel_id)
                if jury_panel:
                    jury_panels.append(jury_panel)

            return jury_panels

    # ===== COMPETITION MANAGEMENT METHODS =====

    async def update_role_entry_status(self, competition_id: int, role: str, is_open: bool) -> CompetitionModel:
        """Обновить статус открытия регистрации для конкретной роли."""
        async with self.get_session() as session:
            competition = await session.get(CompetitionModel, competition_id)
            if competition:
                role_field = f"{role}_entry_open"
                if hasattr(competition, role_field):
                    setattr(competition, role_field, is_open)
                    session.add(competition)
                    await session.commit()
            return competition

    # ===== BROADCAST MANAGEMENT METHODS =====

    async def create_message_template(
        self,
        name: str,
        subject: str,
        body_telegram: str,
        body_email: str,
        available_variables: Dict[str, str],
        description: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> "MessageTemplate":
        """Create a new message template for broadcasts."""
        from models import MessageTemplate
        async with self.get_session() as session:
            template = MessageTemplate(
                name=name,
                subject=subject,
                body_telegram=body_telegram,
                body_email=body_email,
                available_variables=available_variables,
                description=description,
                created_by=created_by,
                is_active=True
            )
            session.add(template)
            await session.commit()
            return template

    async def create_broadcast(
        self,
        name: str,
        template_id: int,
        filters: Dict[str, Any],
        send_telegram: bool = True,
        send_email: bool = False,
        created_by: int = 0
    ) -> "Broadcast":
        """Create a new broadcast campaign."""
        from models import Broadcast, BroadcastStatus
        async with self.get_session() as session:
            broadcast = Broadcast(
                name=name,
                template_id=template_id,
                filters=filters,
                send_telegram=send_telegram,
                send_email=send_email,
                status=BroadcastStatus.draft.value,
                created_by=created_by
            )
            session.add(broadcast)
            await session.commit()
            return broadcast

    async def get_broadcasts(self, status: Optional[str] = None) -> List["Broadcast"]:
        """Get list of broadcasts, optionally filtered by status."""
        from models import Broadcast
        async with self.get_session() as session:
            query = select(Broadcast)
            if status:
                query = query.where(Broadcast.status == status)
            result = await session.execute(query.order_by(Broadcast.created_at.desc()))
            return result.scalars().all()

    async def get_broadcast_by_id(self, broadcast_id: int) -> Optional["Broadcast"]:
        """Get broadcast by ID."""
        from models import Broadcast
        async with self.get_session() as session:
            return await session.get(Broadcast, broadcast_id)

    async def get_broadcast_statistics(self, broadcast_id: int) -> Dict[str, Any]:
        """Get statistics for a broadcast."""
        from models import Broadcast, BroadcastRecipient
        async with self.get_session() as session:
            broadcast = await session.get(Broadcast, broadcast_id)
            if not broadcast:
                return {}

            # Get recipient statistics
            result = await session.execute(
                select(BroadcastRecipient).where(
                    BroadcastRecipient.broadcast_id == broadcast_id
                )
            )
            recipients = result.scalars().all()

            # Calculate stats
            total = len(recipients)
            telegram_sent = sum(1 for r in recipients if r.telegram_status == 'sent')
            email_sent = sum(1 for r in recipients if r.email_status == 'sent')
            failed = sum(1 for r in recipients if r.telegram_status == 'failed' or r.email_status == 'failed')

            return {
                'broadcast_id': broadcast.id,
                'name': broadcast.name,
                'status': broadcast.status.value if hasattr(broadcast.status, 'value') else broadcast.status,
                'total_recipients': total,
                'telegram_sent': telegram_sent,
                'email_sent': email_sent,
                'failed': failed,
                'sent_count': broadcast.sent_count,
                'failed_count': broadcast.failed_count,
                'created_at': broadcast.created_at,
                'started_at': broadcast.started_at,
                'completed_at': broadcast.completed_at
            }

    async def get_message_templates(self, active_only: bool = False) -> List["MessageTemplate"]:
        """Get list of message templates."""
        from models import MessageTemplate
        async with self.get_session() as session:
            query = select(MessageTemplate)
            if active_only:
                query = query.where(MessageTemplate.is_active == True)
            result = await session.execute(query.order_by(MessageTemplate.created_at.desc()))
            return result.scalars().all()


# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()