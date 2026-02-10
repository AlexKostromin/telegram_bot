from typing import Dict, Any, List, Optional, Set
import logging
import re

try:
    from jinja2 import Template, TemplateSyntaxError, UndefinedError, Environment
except ImportError:
    raise ImportError(
        "❌ Jinja2 not installed. Install with: pip install jinja2"
    )

logger = logging.getLogger(__name__)

class TemplateRenderer:

    DEFAULT_VARIABLES: Dict[str, str] = {
        'first_name': 'User first name',
        'last_name': 'User last name',
        'telegram_username': 'User Telegram username',
        'email': 'User email address',
        'phone': 'User phone number',
        'country': 'User country',
        'city': 'User city',
        'club': 'User club or school',
        'company': 'User company',
        'position': 'User position/title',
        'certificate_name': 'Certificate name',
        'presentation': 'Presentation topic',
        'bio': 'User biography',
        'competition_name': 'Competition name',
        'competition_type': 'Competition type',
        'role': 'User role (player, voter, viewer, adviser)',
        'registration_status': 'Registration status (pending, approved, rejected)',
        'date': 'Current date',
        'time': 'Current time',
    }

    def __init__(self):
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)

    def render(
        self,
        template_text: str,
        context: Dict[str, Any],
        strict: bool = False
    ) -> str:
        try:
            template = self.env.from_string(template_text)

            if strict:
                result = template.render(context)
            else:
                safe_context = {k: v for k, v in context.items() if k in self.extract_variables(template_text)}
                result = template.render(**safe_context)

            return result

        except TemplateSyntaxError as e:
            logger.error(f"❌ Template syntax error: {e}")
            raise

        except UndefinedError as e:
            logger.error(f"❌ Undefined variable in template: {e}")
            raise

        except Exception as e:
            logger.error(f"❌ Template rendering error: {e}")
            raise

    def extract_variables(self, template_text: str) -> Set[str]:
        pattern = r'\{\{\s*(\w+)(?:\s*[|].*?)?\s*\}\}'
        matches = re.findall(pattern, template_text)
        return set(matches)

    def validate_template(self, template_text: str) -> tuple[bool, str]:
        try:
            self.env.from_string(template_text)
            return (True, "")
        except TemplateSyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.message}"
            return (False, error_msg)
        except Exception as e:
            return (False, str(e))

    def get_available_variables(self) -> Dict[str, str]:
        return self.DEFAULT_VARIABLES.copy()

    def render_preview(
        self,
        template_text: str,
        sample_data: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Dict[str, str]]:
        variables = self.extract_variables(template_text)

        preview_context = {}
        for var in variables:
            if sample_data and var in sample_data:
                preview_context[var] = sample_data[var]
            elif var in self.DEFAULT_VARIABLES:
                preview_context[var] = f"[{self.DEFAULT_VARIABLES[var]}]"
            else:
                preview_context[var] = f"[{var}]"

        try:
            rendered = self.render(template_text, preview_context)
            return (rendered, preview_context)
        except Exception as e:
            logger.error(f"❌ Preview rendering failed: {e}")
            return (f"[Error: {str(e)}]", {})

    @staticmethod
    def create_sample_context() -> Dict[str, Any]:
        from datetime import datetime

        return {
            'first_name': 'John',
            'last_name': 'Doe',
            'telegram_username': 'johndoe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'country': 'United States',
            'city': 'New York',
            'club': 'Chess Club NYC',
            'company': 'Acme Corp',
            'position': 'Developer',
            'certificate_name': 'Grand Master',
            'presentation': 'The Future of Chess',
            'bio': 'International chess player with 15 years experience',
            'competition_name': 'World Chess Championship 2024',
            'competition_type': 'Online Tournament',
            'role': 'player',
            'registration_status': 'approved',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
        }
