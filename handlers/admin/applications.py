from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.admin_check import admin_only
from utils import db_manager
from utils.notifications import notify_user_approved, notify_user_rejected, notify_admins_new_registration
from utils.helpers import BotHelpers
from keyboards.admin_keyboards import applications_list_keyboard, application_actions_keyboard, confirm_action_keyboard, admin_main_menu_keyboard
from messages import BotMessages
from states import AdminStates

admin_applications_router = Router()

@admin_applications_router.callback_query(F.data == "admin_applications")
@admin_only
async def list_applications_handler(callback: CallbackQuery, state: FSMContext):
    applications = await db_manager.get_pending_registrations()

    if not applications:
        await callback.message.answer(
            BotMessages.ADMIN_NO_PENDING,
            reply_markup=admin_main_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = f"<b>📬 Заявки на рассмотрение</b> ({len(applications)}):"
    await callback.message.answer(
        text,
        reply_markup=applications_list_keyboard(applications),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.viewing_applications_list)
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("app_view_"))
@admin_only
async def view_application_detail(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    reg_data = await db_manager.get_registration_with_user(registration_id)

    if not reg_data:
        await callback.answer("Application not found", show_alert=True)
        return

    text = BotHelpers.format_application_detail(reg_data)

    await callback.message.edit_text(
        text,
        reply_markup=application_actions_keyboard(registration_id, reg_data["status"]),
        parse_mode="HTML"
    )
    await state.update_data(current_application=registration_id)
    await state.set_state(AdminStates.viewing_application_detail)
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("app_approve_"))
@admin_only
async def approve_application_confirm(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    await callback.message.edit_text(
        "<b>✅ Подтвердите одобрение заявки?</b>",
        reply_markup=confirm_action_keyboard("approve", str(registration_id)),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.confirming_action)
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("confirm_approve_"))
@admin_only
async def approve_application_execute(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])
    admin_id = callback.from_user.id

    await db_manager.approve_registration(registration_id, admin_id)

    reg_data = await db_manager.get_registration_with_user(registration_id)

    if reg_data:
        await notify_user_approved(
            callback.bot,
            reg_data["telegram_id"],
            reg_data["competition_name"]
        )

    await callback.message.edit_text(BotMessages.ADMIN_APPLICATION_APPROVED)
    await state.clear()
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("app_reject_"))
@admin_only
async def reject_application_confirm(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    await callback.message.edit_text(
        "❌ Подтвердите отклонение заявки?",
        reply_markup=confirm_action_keyboard("reject", str(registration_id))
    )
    await state.set_state(AdminStates.confirming_action)
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("confirm_reject_"))
@admin_only
async def reject_application_execute(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    await db_manager.reject_registration(registration_id)

    reg_data = await db_manager.get_registration_with_user(registration_id)

    if reg_data:
        await notify_user_rejected(
            callback.bot,
            reg_data["telegram_id"],
            reg_data["competition_name"]
        )

    await callback.message.edit_text(BotMessages.ADMIN_APPLICATION_REJECTED)
    await state.clear()
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("app_revoke_"))
@admin_only
async def revoke_application_confirm(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    await callback.message.edit_text(
        "⚠️ Подтвердите отзыв регистрации?",
        reply_markup=confirm_action_keyboard("revoke", str(registration_id))
    )
    await state.set_state(AdminStates.confirming_action)
    await callback.answer()

@admin_applications_router.callback_query(F.data.startswith("confirm_revoke_"))
@admin_only
async def revoke_application_execute(callback: CallbackQuery, state: FSMContext):
    registration_id = int(callback.data.split("_")[2])

    await db_manager.revoke_registration(registration_id)

    reg_data = await db_manager.get_registration_with_user(registration_id)

    if reg_data:
        from utils.notifications import notify_user_revoked
        await notify_user_revoked(
            callback.bot,
            reg_data["telegram_id"],
            reg_data["competition_name"]
        )

    await callback.message.edit_text("⚠️ Регистрация отозвана")
    await state.clear()
    await callback.answer()
