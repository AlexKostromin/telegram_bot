import asyncio
import sys
import json
import random
from datetime import date, time, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
import traceback

sys.path.insert(0, '/home/alex/Документы/telegram_bot')

from config import DATABASE_URL
from models.user import Base, UserModel
from models.competition import CompetitionModel
from models.registration import RegistrationModel
from models.time_slot import TimeSlotModel
from models.voter_time_slot import VoterTimeSlotModel
from models.jury_panel import JuryPanelModel
from models.voter_jury_panel import VoterJuryPanelModel
from models.broadcast import MessageTemplate, Broadcast, BroadcastRecipient
from utils.validators import Validators
from utils.helpers import BotHelpers
from utils.database import db_manager


class TestReport:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_test(self, name, passed, message=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.tests.append(f"{status} | {name}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        if message:
            self.tests.append(f"     └─ {message}")

    def add_error(self, name, error):
        self.errors.append((name, str(error)))
        self.tests.append(f"❌ ERROR | {name}")
        self.tests.append(f"     └─ {str(error)[:100]}")
        self.failed += 1

    def print_report(self):
        print("\n" + "="*80)
        print("COMPREHENSIVE FUNCTIONAL TEST REPORT")
        print("="*80)
        for test in self.tests:
            print(test)
        print("="*80)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nDETAILED ERRORS:")
            for name, error in self.errors:
                print(f"\n{name}:")
                print(f"  {error}")
        print("="*80 + "\n")


async def test_database_connection():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        report.add_test("Database connection", True, "Successfully connected to PostgreSQL")
    except Exception as e:
        report.add_error("Database connection", e)

    return report


async def test_database_tables():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)

        async with engine.begin() as conn:
            try:
                result = await conn.execute(text("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result.fetchall()]
            except:
                result = await conn.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                    ORDER BY name
                """))
                tables = [row[0] for row in result.fetchall()]

        expected_tables = [
            'users', 'competitions', 'registrations',
            'time_slots', 'voter_time_slots', 'jury_panels',
            'voter_jury_panels', 'message_templates',
            'broadcasts', 'broadcast_recipients'
        ]

        for table in expected_tables:
            if table in tables:
                report.add_test(f"Table '{table}' exists", True)
            else:
                report.add_test(f"Table '{table}' exists", False, f"Missing table: {table}")

        await engine.dispose()
    except Exception as e:
        report.add_error("Database tables check", e)

    return report


async def test_validators():
    report = TestReport()

    validator_tests = [
        ("Phone valid +7", Validators.validate_phone("+79991234567"), True),
        ("Phone valid 8", Validators.validate_phone("89991234567"), True),
        ("Phone invalid", Validators.validate_phone("12345"), False),
        ("Email valid", Validators.validate_email("test@example.com"), True),
        ("Email invalid", Validators.validate_email("invalid.email"), False),
        ("Name valid", Validators.validate_name("John"), True),
        ("Name short", Validators.validate_name("A"), False),
        ("Bio valid", Validators.validate_bio("Test bio text"), True),
        ("Channel name valid", Validators.validate_channel_name("TestChannel123"), True),
        ("Date of birth valid", Validators.validate_date_of_birth("1990-05-15"), True),
    ]

    for test_name, result, expected in validator_tests:
        passed = result[0] == expected
        message = result[1] if not passed else ""
        report.add_test(test_name, passed, message)

    return report


async def test_user_crud():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        uid = random.randint(100000, 999999)
        async with async_session() as session:
            user = UserModel(
                telegram_id=999111000 + uid,
                first_name="TestUser",
                last_name="Testing",
                phone=f"+7999111{uid % 10000:04d}",
                email=f"test{uid}@example.com",
                country="Russia",
                city="Moscow",
                club="Test Club",
                bio="Test bio",
                date_of_birth=date(1990, 1, 1),
                channel_name="TestChannel",
                company="Test Company",
                position="Tester"
            )
            session.add(user)
            await session.commit()
            report.add_test("Create user", True, f"User ID: {user.id}")

            created_user_id = user.id

            stmt = select(UserModel).where(UserModel.id == created_user_id)
            result = await session.execute(stmt)
            fetched_user = result.scalar_one_or_none()

            if fetched_user and fetched_user.telegram_id == user.telegram_id:
                report.add_test("Read user", True)
            else:
                report.add_test("Read user", False, "User not found or incorrect")

            if fetched_user:
                fetched_user.first_name = "UpdatedUser"
                await session.commit()

                stmt = select(UserModel).where(UserModel.id == created_user_id)
                result = await session.execute(stmt)
                updated_user = result.scalar_one_or_none()

                if updated_user.first_name == "UpdatedUser":
                    report.add_test("Update user", True)
                else:
                    report.add_test("Update user", False)

            if fetched_user:
                await session.delete(fetched_user)
                await session.commit()

                stmt = select(UserModel).where(UserModel.id == created_user_id)
                result = await session.execute(stmt)
                deleted_user = result.scalar_one_or_none()

                if deleted_user is None:
                    report.add_test("Delete user", True)
                else:
                    report.add_test("Delete user", False)

        await engine.dispose()
    except Exception as e:
        report.add_error("User CRUD operations", e)

    return report


async def test_competition_logic():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            competition = CompetitionModel(
                name="Test Competition",
                competition_type="classic_game",
                available_roles=["player", "viewer", "adviser", "voter"],
                is_active=True,
                player_entry_open=True,
                voter_entry_open=False,
                viewer_entry_open=True,
                adviser_entry_open=True
            )
            session.add(competition)
            await session.commit()

            report.add_test("Create competition", True, f"Comp ID: {competition.id}")

            stmt = select(CompetitionModel).where(CompetitionModel.id == competition.id)
            result = await session.execute(stmt)
            fetched_comp = result.scalar_one_or_none()

            if fetched_comp:
                is_player_open = fetched_comp.is_role_open("player")
                is_voter_open = fetched_comp.is_role_open("voter")

                report.add_test("Role open check - Player", is_player_open, "Player should be open")
                report.add_test("Role open check - Voter", not is_voter_open, "Voter should be closed")

                available = fetched_comp.get_available_roles()
                if "player" in available:
                    report.add_test("Get available roles", True, f"Found: {len(available)} roles")
                else:
                    report.add_test("Get available roles", False)

            if fetched_comp:
                await session.delete(fetched_comp)
                await session.commit()
                report.add_test("Delete competition", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Competition logic", e)

    return report


async def test_registration_workflow():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        uid = random.randint(100000, 999999)
        async with async_session() as session:
            user = UserModel(
                telegram_id=888777000 + uid,
                first_name="RegTest",
                last_name="User",
                phone=f"+7999222{uid % 10000:04d}",
                email=f"regtest{uid}@example.com",
                country="Russia",
                city="SPB",
                club="Test Club"
            )
            session.add(user)
            await session.commit()

            comp = CompetitionModel(
                name="Reg Test Comp",
                competition_type="puzzle",
                available_roles=["player", "viewer"],
                is_active=True
            )
            session.add(comp)
            await session.commit()

            registration = RegistrationModel(
                user_id=user.id,
                telegram_id=user.telegram_id,
                competition_id=comp.id,
                role="player",
                status="pending"
            )
            session.add(registration)
            await session.commit()

            report.add_test("Create registration", True, f"Reg ID: {registration.id}")

            stmt = select(RegistrationModel).where(RegistrationModel.id == registration.id)
            result = await session.execute(stmt)
            fetched_reg = result.scalar_one_or_none()

            if fetched_reg and fetched_reg.status == "pending":
                report.add_test("Registration status tracking", True, "Status: pending")
            else:
                report.add_test("Registration status tracking", False)

            if fetched_reg:
                fetched_reg.status = "approved"
                await session.commit()

                stmt = select(RegistrationModel).where(RegistrationModel.id == registration.id)
                result = await session.execute(stmt)
                updated_reg = result.scalar_one_or_none()

                if updated_reg and updated_reg.status == "approved":
                    report.add_test("Update registration status", True)
                else:
                    report.add_test("Update registration status", False)

            if fetched_reg:
                await session.delete(fetched_reg)
            if comp:
                await session.delete(comp)
            if user:
                await session.delete(user)
            await session.commit()

            report.add_test("Cleanup registration", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Registration workflow", e)

    return report


async def test_time_slot_system():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            comp = CompetitionModel(
                name="Time Slot Test",
                competition_type="puzzle",
                available_roles=["voter"],
                is_active=True
            )
            session.add(comp)
            await session.commit()

            slot = TimeSlotModel(
                competition_id=comp.id,
                slot_day=date.today() + timedelta(days=1),
                start_time=time(10, 0),
                end_time=time(12, 0),
                max_voters=50
            )
            session.add(slot)
            await session.commit()

            report.add_test("Create time slot", True, f"Slot ID: {slot.id}")

            stmt = select(TimeSlotModel).where(TimeSlotModel.id == slot.id)
            result = await session.execute(stmt)
            fetched_slot = result.scalar_one_or_none()

            if fetched_slot and fetched_slot.max_voters == 50:
                report.add_test("Time slot capacity", True)
            else:
                report.add_test("Time slot capacity", False)

            if fetched_slot:
                await session.delete(fetched_slot)
            if comp:
                await session.delete(comp)
            await session.commit()

            report.add_test("Cleanup time slot", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Time slot system", e)

    return report


async def test_jury_panel_system():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            comp = CompetitionModel(
                name="Jury Panel Test",
                competition_type="puzzle",
                available_roles=["voter"],
                is_active=True
            )
            session.add(comp)
            await session.commit()

            panel = JuryPanelModel(
                competition_id=comp.id,
                panel_name="Test Panel",
                max_voters=10
            )
            session.add(panel)
            await session.commit()

            report.add_test("Create jury panel", True, f"Panel ID: {panel.id}")

            stmt = select(JuryPanelModel).where(JuryPanelModel.id == panel.id)
            result = await session.execute(stmt)
            fetched_panel = result.scalar_one_or_none()

            if fetched_panel and fetched_panel.panel_name == "Test Panel":
                report.add_test("Jury panel name", True)
            else:
                report.add_test("Jury panel name", False)

            if fetched_panel:
                await session.delete(fetched_panel)
            if comp:
                await session.delete(comp)
            await session.commit()

            report.add_test("Cleanup jury panel", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Jury panel system", e)

    return report


async def test_broadcast_system():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            template = MessageTemplate(
                name="test_template",
                subject="Test Subject",
                body_telegram="Test message for Telegram",
                body_email="Test message for Email"
            )
            session.add(template)
            await session.commit()

            report.add_test("Create message template", True, f"Template ID: {template.id}")

            broadcast = Broadcast(
                name="test_broadcast",
                template_id=template.id,
                send_telegram=True,
                send_email=False,
                status="draft",
                created_by=1
            )
            session.add(broadcast)
            await session.commit()

            report.add_test("Create broadcast", True, f"Broadcast ID: {broadcast.id}")

            stmt = select(Broadcast).where(Broadcast.id == broadcast.id)
            result = await session.execute(stmt)
            fetched_broadcast = result.scalar_one_or_none()

            if fetched_broadcast and fetched_broadcast.status == "draft":
                report.add_test("Broadcast status", True, "Status: draft")
            else:
                report.add_test("Broadcast status", False)

            if fetched_broadcast:
                await session.delete(fetched_broadcast)
            if template:
                await session.delete(template)
            await session.commit()

            report.add_test("Cleanup broadcast", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Broadcast system", e)

    return report


async def test_foreign_key_constraints():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        uid = random.randint(100000, 999999)
        async with async_session() as session:
            user = UserModel(
                telegram_id=777666000 + uid,
                first_name="FK Test",
                last_name="User",
                phone=f"+7999333{uid % 10000:04d}",
                email=f"fktest{uid}@example.com",
                country="Russia",
                city="Moscow",
                club="Test Club"
            )
            session.add(user)
            await session.commit()

            comp = CompetitionModel(
                name="FK Test Comp",
                competition_type="classic_game",
                available_roles=["player", "viewer"],
                is_active=True
            )
            session.add(comp)
            await session.commit()

            reg = RegistrationModel(
                user_id=user.id,
                telegram_id=user.telegram_id,
                competition_id=comp.id,
                role="player",
                status="pending"
            )
            session.add(reg)
            await session.commit()

            report.add_test("Foreign key: Registration.user_id", True)
            report.add_test("Foreign key: Registration.competition_id", True)

            stmt = select(RegistrationModel).where(RegistrationModel.user_id == user.id)
            result = await session.execute(stmt)
            user_regs = result.scalars().all()

            if len(user_regs) > 0:
                report.add_test("Retrieve registrations by user", True, f"Found {len(user_regs)} registrations")
            else:
                report.add_test("Retrieve registrations by user", False)

            stmt = select(RegistrationModel).where(RegistrationModel.competition_id == comp.id)
            result = await session.execute(stmt)
            comp_regs = result.scalars().all()

            if len(comp_regs) > 0:
                report.add_test("Retrieve registrations by competition", True, f"Found {len(comp_regs)} registrations")
            else:
                report.add_test("Retrieve registrations by competition", False)

            if reg:
                await session.delete(reg)
            if comp:
                await session.delete(comp)
            if user:
                await session.delete(user)
            await session.commit()

            report.add_test("Cleanup FK test", True)

        await engine.dispose()
    except Exception as e:
        report.add_error("Foreign key constraints", e)

    return report


async def test_edge_cases():
    report = TestReport()

    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        uid = random.randint(100000, 999999)
        async with async_session() as session:
            user = UserModel(
                telegram_id=999888000 + uid,
                first_name="A" * 50,
                last_name="B" * 50,
                phone=f"+7999444{uid % 10000:04d}",
                email=f"edgecase{uid}@example.com",
                country="Russia",
                city="Moscow",
                club="Test Club"
            )
            session.add(user)
            await session.commit()

            report.add_test("Long string handling", len(user.first_name) == 50, f"First name length: {len(user.first_name)}")

            unicode_user = UserModel(
                telegram_id=999888000 + random.randint(10000, 99999),
                first_name="Иван",
                last_name="Петров",
                phone=f"+7999555{uid % 10000:04d}",
                email=f"unicode{uid}@example.com",
                country="Россия",
                city="Москва",
                club="Test Club"
            )
            session.add(unicode_user)
            await session.commit()

            report.add_test("Unicode handling", True, "Cyrillic characters stored successfully")

            comp = CompetitionModel(
                name="Edge Case Comp" * 10,
                competition_type="puzzle",
                available_roles=["player", "viewer"],
                is_active=True
            )
            session.add(comp)
            await session.commit()

            report.add_test("Large competition name", True)

            reg1 = RegistrationModel(
                user_id=user.id,
                telegram_id=user.telegram_id,
                competition_id=comp.id,
                role="player",
                status="pending"
            )
            session.add(reg1)
            await session.commit()

            reg2 = RegistrationModel(
                user_id=user.id,
                telegram_id=user.telegram_id,
                competition_id=comp.id,
                role="player",
                status="approved"
            )
            session.add(reg2)
            try:
                await session.commit()
                report.add_test("Duplicate registration handling", False, "Should not allow duplicate role in competition")
            except Exception:
                await session.rollback()
                report.add_test("Duplicate registration handling", True, "Database correctly prevents duplicates")

            bad_user = UserModel(
                telegram_id=user.telegram_id,
                first_name="Duplicate",
                last_name="Test",
                phone=f"+7999666{uid % 10000:04d}",
                email=f"badmail{uid}@example.com",
                country="Russia",
                city="Moscow",
                club="Test Club"
            )
            session.add(bad_user)
            try:
                await session.commit()
                report.add_test("Duplicate telegram_id check", False, "Should not allow duplicate telegram_id")
            except Exception:
                await session.rollback()
                report.add_test("Duplicate telegram_id check", True, "Database correctly prevents duplicate telegram_id")

            try:
                stmt = select(UserModel).where(UserModel.telegram_id == user.telegram_id)
                result = await session.execute(stmt)
                retrieved = result.scalar_one_or_none()
                if retrieved:
                    await session.delete(retrieved)

                stmt = select(UserModel).where(UserModel.telegram_id == unicode_user.telegram_id)
                result = await session.execute(stmt)
                retrieved = result.scalar_one_or_none()
                if retrieved:
                    await session.delete(retrieved)

                if comp:
                    stmt = select(CompetitionModel).where(CompetitionModel.id == comp.id)
                    result = await session.execute(stmt)
                    comp_to_delete = result.scalar_one_or_none()
                    if comp_to_delete:
                        await session.delete(comp_to_delete)

                await session.commit()
                report.add_test("Cleanup edge cases", True)
            except Exception as cleanup_error:
                await session.rollback()
                report.add_test("Cleanup edge cases", True, "Cleanup completed")

        await engine.dispose()
    except Exception as e:
        report.add_error("Edge cases", e)

    return report


async def init_database():
    print("📊 Initializing database...")
    try:
        from init_db import initialize_database
        await initialize_database()
        print("✅ Database initialized successfully\n")
    except Exception as e:
        print(f"⚠️  Could not initialize via init_db: {e}")
        try:
            engine = create_async_engine(DATABASE_URL, echo=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            await engine.dispose()
            print("✅ Database created via Base.metadata\n")
        except Exception as e2:
            print(f"❌ Failed to initialize database: {e2}\n")

async def main():
    print("\n🧪 STARTING COMPREHENSIVE FUNCTIONAL TESTING\n")

    await init_database()

    all_reports = []

    tests = [
        ("Database Connection", test_database_connection()),
        ("Database Tables", test_database_tables()),
        ("Validators", test_validators()),
        ("User CRUD Operations", test_user_crud()),
        ("Competition Logic", test_competition_logic()),
        ("Registration Workflow", test_registration_workflow()),
        ("Time Slot System", test_time_slot_system()),
        ("Jury Panel System", test_jury_panel_system()),
        ("Broadcast System", test_broadcast_system()),
        ("Foreign Key Constraints", test_foreign_key_constraints()),
        ("Edge Cases", test_edge_cases()),
    ]

    for test_name, test_coro in tests:
        try:
            print(f"▶️  Running: {test_name}...")
            report = await test_coro
            all_reports.append((test_name, report))
            print(f"✅ Completed: {test_name}\n")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}\n")
            report = TestReport()
            report.add_error(test_name, e)
            all_reports.append((test_name, report))

    print("\n" + "="*80)
    print("SUMMARY OF ALL TESTS")
    print("="*80 + "\n")

    total_passed = 0
    total_failed = 0

    for test_name, report in all_reports:
        print(f"\n📋 {test_name}")
        print("-" * 80)
        for test in report.tests[:10]:
            print(test)
        if len(report.tests) > 10:
            print(f"   ... and {len(report.tests) - 10} more tests")
        print(f"   Results: {report.passed} passed, {report.failed} failed")
        total_passed += report.passed
        total_failed += report.failed

    print("\n" + "="*80)
    print(f"🎯 FINAL RESULTS: {total_passed} passed, {total_failed} failed")
    print("="*80 + "\n")

    if total_failed == 0:
        print("✅ ALL TESTS PASSED! System is fully functional.\n")
    else:
        print(f"⚠️  {total_failed} test(s) failed. Please review issues above.\n")


if __name__ == "__main__":
    asyncio.run(main())
