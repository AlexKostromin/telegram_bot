from typing import Dict, Any, List, Optional
import logging
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserModel, RegistrationModel, CompetitionModel, RegistrationStatus

logger = logging.getLogger(__name__)

class RecipientFilter:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_recipients(
        self,
        competition_ids: Optional[List[int]] = None,
        roles: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        cities: Optional[List[str]] = None,
        has_email: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        try:

            query = select(
                UserModel.id,
                UserModel.telegram_id,
                UserModel.email,
                UserModel.first_name,
                UserModel.last_name,
                UserModel.phone,
                UserModel.country,
                UserModel.city,
                UserModel.club,
                UserModel.company,
                UserModel.position,
                RegistrationModel.id.label("registration_id"),
                RegistrationModel.role,
                RegistrationModel.status,
                CompetitionModel.name.label("competition_name"),
            ).join(
                RegistrationModel,
                UserModel.id == RegistrationModel.user_id,
                isouter=True
            ).join(
                CompetitionModel,
                RegistrationModel.competition_id == CompetitionModel.id,
                isouter=True
            )

            conditions = []

            if competition_ids:
                conditions.append(RegistrationModel.competition_id.in_(competition_ids))

            if roles:
                conditions.append(RegistrationModel.role.in_(roles))

            if statuses:

                status_enums = [
                    RegistrationStatus(s) if isinstance(s, str) else s
                    for s in statuses
                ]
                conditions.append(RegistrationModel.status.in_(status_enums))

            if countries:
                conditions.append(UserModel.country.in_(countries))

            if cities:
                conditions.append(UserModel.city.in_(cities))

            if has_email:
                conditions.append(UserModel.email.isnot(None))
                conditions.append(UserModel.email != '')

            if conditions:
                query = query.where(and_(*conditions))

            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            result = await self.session.execute(query)
            rows = result.fetchall()

            recipients = []
            for row in rows:
                recipients.append({
                    'user_id': row.id,
                    'telegram_id': row.telegram_id,
                    'email': row.email,
                    'first_name': row.first_name,
                    'last_name': row.last_name,
                    'phone': row.phone,
                    'country': row.country,
                    'city': row.city,
                    'club': row.club,
                    'company': row.company,
                    'position': row.position,
                    'registration_id': row.registration_id,
                    'role': row.role,
                    'status': row.status.value if row.status else None,
                    'competition_name': row.competition_name,
                })

            logger.info(f"✅ Found {len(recipients)} recipients matching filters")
            return recipients

        except Exception as e:
            logger.error(f"❌ Error filtering recipients: {e}")
            raise

    async def count_recipients(
        self,
        competition_ids: Optional[List[int]] = None,
        roles: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        cities: Optional[List[str]] = None,
        has_email: bool = False,
    ) -> int:
        try:

            from sqlalchemy import func

            query = select(func.count(UserModel.id)).distinct()

            query = query.join(
                RegistrationModel,
                UserModel.id == RegistrationModel.user_id,
                isouter=True
            ).join(
                CompetitionModel,
                RegistrationModel.competition_id == CompetitionModel.id,
                isouter=True
            )

            conditions = []

            if competition_ids:
                conditions.append(RegistrationModel.competition_id.in_(competition_ids))

            if roles:
                conditions.append(RegistrationModel.role.in_(roles))

            if statuses:
                status_enums = [
                    RegistrationStatus(s) if isinstance(s, str) else s
                    for s in statuses
                ]
                conditions.append(RegistrationModel.status.in_(status_enums))

            if countries:
                conditions.append(UserModel.country.in_(countries))

            if cities:
                conditions.append(UserModel.city.in_(cities))

            if has_email:
                conditions.append(UserModel.email.isnot(None))
                conditions.append(UserModel.email != '')

            if conditions:
                query = query.where(and_(*conditions))

            result = await self.session.execute(query)
            count = result.scalar()

            return count or 0

        except Exception as e:
            logger.error(f"❌ Error counting recipients: {e}")
            return 0

    async def get_available_filters(self) -> Dict[str, Any]:
        try:

            comp_result = await self.session.execute(
                select(CompetitionModel.id, CompetitionModel.name).distinct()
            )
            competitions = [
                {'id': row.id, 'name': row.name}
                for row in comp_result.fetchall()
            ]

            role_result = await self.session.execute(
                select(RegistrationModel.role).distinct().where(
                    RegistrationModel.role.isnot(None)
                )
            )
            roles = [row.role for row in role_result.fetchall() if row.role]

            country_result = await self.session.execute(
                select(UserModel.country).distinct().order_by(UserModel.country)
            )
            countries = [row.country for row in country_result.fetchall() if row.country]

            city_result = await self.session.execute(
                select(UserModel.city).distinct().order_by(UserModel.city)
            )
            cities = [row.city for row in city_result.fetchall() if row.city]

            return {
                'competitions': competitions,
                'roles': roles,
                'statuses': [s.value for s in RegistrationStatus],
                'countries': countries,
                'cities': cities,
            }

        except Exception as e:
            logger.error(f"❌ Error getting available filters: {e}")
            return {
                'competitions': [],
                'roles': [],
                'statuses': [],
                'countries': [],
                'cities': [],
            }

    async def get_sample_recipients(self, limit: int = 5) -> List[Dict[str, Any]]:
        return await self.get_recipients(limit=limit)
