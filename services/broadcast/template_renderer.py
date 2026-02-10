"""
Template renderer for broadcast messages.

Uses Jinja2 for flexible variable substitution in message templates.
Supports conditional logic, filters, and default values.
"""
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
    """
    Render message templates with variable substitution using Jinja2.

    Features:
    - Variable substitution: {{variable_name}}
    - Default values: {{variable | default('default_value')}}
    - String filters: {{text | upper}}, {{text | lower}}
    - Conditional blocks: {% if condition %} ... {% endif %}
    - Template validation and variable extraction

    Example:
        >>> renderer = TemplateRenderer()
        >>> context = {
        ...     'first_name': 'John',
        ...     'competition_name': 'Chess Tournament 2024'
        ... }
        >>> rendered = renderer.render(
        ...     'Welcome {{ first_name }} to {{ competition_name }}!',
        ...     context
        ... )
        >>> print(rendered)
        Welcome John to Chess Tournament 2024!
    """

    # Default available variables for templates
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
        """Initialize template renderer with Jinja2 environment."""
        self.env = Environment(trim_blocks=True, lstrip_blocks=True)

    def render(
        self,
        template_text: str,
        context: Dict[str, Any],
        strict: bool = False
    ) -> str:
        """
        Render template with provided context.

        Args:
            template_text: Template text with {{ }} variables
            context: Dictionary with variable values
            strict: If True, raise error on undefined variables; if False, use empty string

        Returns:
            Rendered template text with variables substituted

        Raises:
            TemplateSyntaxError: If template syntax is invalid
            UndefinedError: If strict=True and variable is undefined

        Example:
            >>> renderer = TemplateRenderer()
            >>> rendered = renderer.render(
            ...     'Hello {{ name }}, your score is {{ score }}',
            ...     {'name': 'Alice', 'score': 95}
            ... )
            >>> print(rendered)
            Hello Alice, your score is 95
        """
        try:
            # Create Jinja2 template
            template = self.env.from_string(template_text)

            # Render with context
            if strict:
                # Strict mode: fail on undefined variables
                result = template.render(context)
            else:
                # Lenient mode: use empty string for undefined variables
                # Filter context to only include variables in template
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
        """
        Extract all variables from template.

        Args:
            template_text: Template text with {{ }} variables

        Returns:
            Set of variable names used in template

        Example:
            >>> renderer = TemplateRenderer()
            >>> vars = renderer.extract_variables(
            ...     'Hello {{ first_name }} {{ last_name }}'
            ... )
            >>> print(vars)
            {'first_name', 'last_name'}
        """
        # Find all {{ variable }} patterns
        pattern = r'\{\{\s*(\w+)(?:\s*[|].*?)?\s*\}\}'
        matches = re.findall(pattern, template_text)
        return set(matches)

    def validate_template(self, template_text: str) -> tuple[bool, str]:
        """
        Validate template syntax without rendering.

        Args:
            template_text: Template text to validate

        Returns:
            Tuple (is_valid: bool, error_message: str)

        Example:
            >>> renderer = TemplateRenderer()
            >>> valid, error = renderer.validate_template('{{ name }')
            >>> print(f"Valid: {valid}, Error: {error}")
            Valid: False, Error: unexpected end of template
        """
        try:
            self.env.from_string(template_text)
            return (True, "")
        except TemplateSyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.message}"
            return (False, error_msg)
        except Exception as e:
            return (False, str(e))

    def get_available_variables(self) -> Dict[str, str]:
        """
        Get list of all available template variables.

        Returns:
            Dictionary with variable names and descriptions

        Example:
            >>> renderer = TemplateRenderer()
            >>> vars = renderer.get_available_variables()
            >>> for name, desc in vars.items():
            ...     print(f"{name}: {desc}")
        """
        return self.DEFAULT_VARIABLES.copy()

    def render_preview(
        self,
        template_text: str,
        sample_data: Optional[Dict[str, Any]] = None
    ) -> tuple[str, Dict[str, str]]:
        """
        Render template preview with sample data.

        Useful for admin panel preview before sending actual broadcast.

        Args:
            template_text: Template text to render
            sample_data: Sample data dict (optional, uses defaults if not provided)

        Returns:
            Tuple (rendered_text: str, used_variables: Dict[str, Any])

        Example:
            >>> renderer = TemplateRenderer()
            >>> preview, vars = renderer.render_preview(
            ...     'Hello {{ first_name }}'
            ... )
            >>> print(preview)
            Hello User first name
        """
        # Extract variables from template
        variables = self.extract_variables(template_text)

        # Create preview context
        preview_context = {}
        for var in variables:
            if sample_data and var in sample_data:
                preview_context[var] = sample_data[var]
            elif var in self.DEFAULT_VARIABLES:
                # Use variable description as preview
                preview_context[var] = f"[{self.DEFAULT_VARIABLES[var]}]"
            else:
                # Unknown variable
                preview_context[var] = f"[{var}]"

        # Render
        try:
            rendered = self.render(template_text, preview_context)
            return (rendered, preview_context)
        except Exception as e:
            logger.error(f"❌ Preview rendering failed: {e}")
            return (f"[Error: {str(e)}]", {})

    @staticmethod
    def create_sample_context() -> Dict[str, Any]:
        """
        Create sample context for template testing.

        Returns:
            Dictionary with sample values for all variables

        Example:
            >>> context = TemplateRenderer.create_sample_context()
            >>> print(context['first_name'])
            John
        """
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
