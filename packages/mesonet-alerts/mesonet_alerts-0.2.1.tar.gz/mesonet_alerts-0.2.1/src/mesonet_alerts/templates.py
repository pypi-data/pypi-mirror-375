"""
Email templates for mesonet alerts.

Provides HTML and plaintext templates using Jinja2 with inline CSS for maximum compatibility.
All templates support consistent variable context for flexibility.
"""

from typing import Dict, Any
import jinja2

# HTML Templates with inline CSS for maximum email client compatibility
HTML_TEMPLATES = {
    "process_failure": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Process Failure Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #dc3545; padding: 20px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">🚨 Process Failure</h1>
                            <p style="margin: 5px 0 0 0; color: #ffffff; opacity: 0.9; font-size: 14px;">{{ stage|title }} Stage Alert</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <!-- Severity Badge -->
                            <div style="margin-bottom: 20px;">
                                <span style="background-color: #dc3545; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{{ severity }}</span>
                            </div>
                            
                            <!-- Main Info -->
                            <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">Provider: {{ provider }}</h2>
                            
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Run ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ run_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Trace ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ trace_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Attempts:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ attempts or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Timestamp:</td>
                                    <td style="padding: 8px 0; color: #333333; font-size: 14px;">{{ timestamp_iso or 'N/A' }}</td>
                                </tr>
                            </table>
                            
                            <!-- Error Details -->
                            {% if error %}
                            <h3 style="margin: 20px 0 10px 0; color: #333333; font-size: 16px; font-weight: 600;">Error Details:</h3>
                            <div style="background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; color: #333333; word-break: break-all;">
                                {{ error }}
                            </div>
                            {% endif %}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; border-top: 1px solid #eeeeee;">
                            <p style="margin: 0; color: #666666; font-size: 12px; text-align: center;">
                                This is an automated message from the Mesonet Alert System.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""",

    "provider_empty_data": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empty Data Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #ffc107; padding: 20px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #333333; font-size: 24px; font-weight: 600;">⚠️ Empty Data Warning</h1>
                            <p style="margin: 5px 0 0 0; color: #333333; opacity: 0.8; font-size: 14px;">{{ stage|title }} Stage Alert</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <!-- Severity Badge -->
                            <div style="margin-bottom: 20px;">
                                <span style="background-color: #ffc107; color: #333333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{{ severity }}</span>
                            </div>
                            
                            <!-- Main Info -->
                            <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">Provider: {{ provider }}</h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                The provider returned no data after {{ attempts or 'multiple' }} attempts. This may indicate a temporary issue with the data source.
                            </p>
                            
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Run ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ run_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Trace ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ trace_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Timestamp:</td>
                                    <td style="padding: 8px 0; color: #333333; font-size: 14px;">{{ timestamp_iso or 'N/A' }}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; border-top: 1px solid #eeeeee;">
                            <p style="margin: 0; color: #666666; font-size: 12px; text-align: center;">
                                This is an automated message from the Mesonet Alert System.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""",

    "harmonize_failure": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Harmonization Failure</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #dc3545; padding: 20px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">🔧 Harmonization Failure</h1>
                            <p style="margin: 5px 0 0 0; color: #ffffff; opacity: 0.9; font-size: 14px;">Data Processing Error</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <!-- Severity Badge -->
                            <div style="margin-bottom: 20px;">
                                <span style="background-color: #dc3545; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{{ severity }}</span>
                            </div>
                            
                            <!-- Main Info -->
                            <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">Provider: {{ provider }}</h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                Failed to harmonize weather data. This may indicate issues with data format, field mappings, or transformation rules.
                            </p>
                            
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Run ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ run_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Trace ID:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ trace_id or 'N/A' }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Timestamp:</td>
                                    <td style="padding: 8px 0; color: #333333; font-size: 14px;">{{ timestamp_iso or 'N/A' }}</td>
                                </tr>
                            </table>
                            
                            <!-- Error Details -->
                            {% if error %}
                            <h3 style="margin: 20px 0 10px 0; color: #333333; font-size: 16px; font-weight: 600;">Error Details:</h3>
                            <div style="background-color: #f8f9fa; border-left: 4px solid #dc3545; padding: 15px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 13px; color: #333333; word-break: break-all;">
                                {{ error }}
                            </div>
                            {% endif %}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; border-top: 1px solid #eeeeee;">
                            <p style="margin: 0; color: #666666; font-size: 12px; text-align: center;">
                                This is an automated message from the Mesonet Alert System.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""",

    "volume_drop": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volume Drop Alert</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: {% if drop_pct and drop_pct|float >= 40 %}#dc3545{% else %}#ffc107{% endif %}; padding: 20px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: {% if drop_pct and drop_pct|float >= 40 %}#ffffff{% else %}#000000{% endif %}; font-size: 24px; font-weight: 600;">
                                {% if drop_pct and drop_pct|float >= 40 %}🚨{% else %}⚠️{% endif %} Volume Drop Detected
                            </h1>
                            <p style="margin: 5px 0 0 0; color: {% if drop_pct and drop_pct|float >= 40 %}#ffffff{% else %}#000000{% endif %}; opacity: 0.9; font-size: 14px;">
                                {% if drop_pct and drop_pct|float >= 40 %}Critical{% else %}Warning{% endif %} Data Volume Alert
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 30px;">
                            <!-- Severity Badge -->
                            <div style="margin-bottom: 20px;">
                                <span style="background-color: {% if drop_pct and drop_pct|float >= 40 %}#dc3545{% else %}#ffc107{% endif %}; color: {% if drop_pct and drop_pct|float >= 40 %}#ffffff{% else %}#000000{% endif %}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                                    {% if drop_pct and drop_pct|float >= 40 %}CRITICAL{% else %}WARNING{% endif %} - {{ drop_pct or 'N/A' }}% DROP
                                </span>
                            </div>
                            
                            <!-- Main Info -->
                            <h2 style="margin: 0 0 15px 0; color: #333333; font-size: 18px; font-weight: 600;">Provider: {{ provider }}</h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                {% if drop_pct and drop_pct|float >= 40 %}
                                <strong>Critical volume drop detected!</strong> This indicates a severe issue with the data provider or pipeline that requires immediate attention.
                                {% else %}
                                Significant drop in data volume detected. This may indicate provider issues or data pipeline problems that should be investigated.
                                {% endif %}
                            </p>
                            
                            <!-- Volume Stats -->
                            <div style="background-color: {% if drop_pct and drop_pct|float >= 40 %}#f8d7da{% else %}#fff3cd{% endif %}; border: 1px solid {% if drop_pct and drop_pct|float >= 40 %}#f5c6cb{% else %}#ffeaa7{% endif %}; border-radius: 6px; padding: 20px; margin-bottom: 20px;">
                                <h3 style="margin: 0 0 15px 0; color: {% if drop_pct and drop_pct|float >= 40 %}#721c24{% else %}#856404{% endif %}; font-size: 16px; font-weight: 600;">Volume Statistics</h3>
                                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                    <tr>
                                        <td style="padding: 5px 0; width: 30%; color: {% if drop_pct and drop_pct|float >= 40 %}#721c24{% else %}#856404{% endif %}; font-size: 14px; font-weight: 500;">Expected:</td>
                                        <td style="padding: 5px 0; color: #333333; font-size: 14px; font-weight: 600;">{{ expected or 'N/A' }} records</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; width: 30%; color: {% if drop_pct and drop_pct|float >= 40 %}#721c24{% else %}#856404{% endif %}; font-size: 14px; font-weight: 500;">Actual:</td>
                                        <td style="padding: 5px 0; color: #333333; font-size: 14px; font-weight: 600;">{{ actual or 'N/A' }} records</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; width: 30%; color: {% if drop_pct and drop_pct|float >= 40 %}#721c24{% else %}#856404{% endif %}; font-size: 14px; font-weight: 500;">Drop:</td>
                                        <td style="padding: 5px 0; color: {% if drop_pct and drop_pct|float >= 40 %}#dc3545{% else %}#e67e22{% endif %}; font-size: 16px; font-weight: 700;">{{ drop_pct or 'N/A' }}%</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 5px 0; width: 30%; color: {% if drop_pct and drop_pct|float >= 40 %}#721c24{% else %}#856404{% endif %}; font-size: 14px; font-weight: 500;">Severity:</td>
                                        <td style="padding: 5px 0; color: {% if drop_pct and drop_pct|float >= 40 %}#dc3545{% else %}#e67e22{% endif %}; font-size: 14px; font-weight: 600;">
                                            {% if drop_pct and drop_pct|float >= 40 %}🚨 CRITICAL{% else %}⚠️ WARNING{% endif %}
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Time Window:</td>
                                    <td style="padding: 8px 0; border-bottom: 1px solid #eeeeee; color: #333333; font-size: 14px;">{{ window_start }} - {{ window_end }}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; width: 30%; color: #666666; font-size: 14px; font-weight: 500;">Timestamp:</td>
                                    <td style="padding: 8px 0; color: #333333; font-size: 14px;">{{ timestamp_iso or 'N/A' }}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; border-top: 1px solid #eeeeee;">
                            <p style="margin: 0; color: #666666; font-size: 12px; text-align: center;">
                                This is an automated message from the Mesonet Alert System.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
}

# Plain text templates
TEXT_TEMPLATES = {
    "process_failure": """
PROCESS FAILURE ALERT
{{ stage|upper }} STAGE - {{ severity }}

Provider: {{ provider }}
Run ID: {{ run_id or 'N/A' }}
Trace ID: {{ trace_id or 'N/A' }}
Attempts: {{ attempts or 'N/A' }}
Timestamp: {{ timestamp_iso or 'N/A' }}

{% if error %}
Error Details:
{{ error }}
{% endif %}

---
This is an automated message from the Mesonet Alert System.
""",

    "provider_empty_data": """
EMPTY DATA WARNING
{{ stage|upper }} STAGE - {{ severity }}

Provider: {{ provider }}
Run ID: {{ run_id or 'N/A' }}
Trace ID: {{ trace_id or 'N/A' }}
Timestamp: {{ timestamp_iso or 'N/A' }}

The provider returned no data after {{ attempts or 'multiple' }} attempts.
This may indicate a temporary issue with the data source.

---
This is an automated message from the Mesonet Alert System.
""",

    "harmonize_failure": """
HARMONIZATION FAILURE
DATA PROCESSING ERROR - {{ severity }}

Provider: {{ provider }}
Run ID: {{ run_id or 'N/A' }}
Trace ID: {{ trace_id or 'N/A' }}
Timestamp: {{ timestamp_iso or 'N/A' }}

Failed to harmonize weather data. This may indicate issues with data format,
field mappings, or transformation rules.

{% if error %}
Error Details:
{{ error }}
{% endif %}

---
This is an automated message from the Mesonet Alert System.
""",

    "volume_drop": """
{% if drop_pct and drop_pct|float >= 40 %}🚨 CRITICAL VOLUME DROP DETECTED{% else %}⚠️ VOLUME DROP DETECTED{% endif %}
DATA VOLUME ALERT - {% if drop_pct and drop_pct|float >= 40 %}CRITICAL{% else %}WARNING{% endif %}

Provider: {{ provider }}
Time Window: {{ window_start }} - {{ window_end }}
Timestamp: {{ timestamp_iso or 'N/A' }}

Volume Statistics:
- Expected: {{ expected or 'N/A' }} records
- Actual: {{ actual or 'N/A' }} records
- Drop: {{ drop_pct or 'N/A' }}%
- Severity: {% if drop_pct and drop_pct|float >= 40 %}🚨 CRITICAL (>40% drop){% else %}⚠️ WARNING (20-40% drop){% endif %}

{% if drop_pct and drop_pct|float >= 40 %}
CRITICAL ALERT: Severe volume drop detected! This indicates a major issue 
with the data provider or pipeline that requires IMMEDIATE attention.
{% else %}
Significant drop in data volume detected. This may indicate provider issues
or data pipeline problems that should be investigated.
{% endif %}

---
This is an automated message from the Mesonet Alert System.
"""
}


def render_html(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render HTML email template with given context.
    
    Args:
        template_name: Name of the template (e.g., 'process_failure')
        context: Template variables dictionary
        
    Returns:
        str: Rendered HTML content
        
    Raises:
        KeyError: If template name doesn't exist
        jinja2.TemplateError: If template rendering fails
    """
    if template_name not in HTML_TEMPLATES:
        raise KeyError(f"HTML template '{template_name}' not found")
    
    template = jinja2.Template(HTML_TEMPLATES[template_name])
    return template.render(**context)


def render_text(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render plaintext email template with given context.
    
    Args:
        template_name: Name of the template (e.g., 'process_failure')
        context: Template variables dictionary
        
    Returns:
        str: Rendered plaintext content
        
    Raises:
        KeyError: If template name doesn't exist
        jinja2.TemplateError: If template rendering fails
    """
    if template_name not in TEXT_TEMPLATES:
        raise KeyError(f"Text template '{template_name}' not found")
    
    template = jinja2.Template(TEXT_TEMPLATES[template_name])
    return template.render(**context)


# TODO: Future database-backed template overrides
# class TemplateRepo:
#     """Repository for fetching custom templates from database."""
#     
#     @staticmethod
#     def get(template_name: str, format_type: str = "html") -> Optional[str]:
#         """
#         Get custom template from database.
#         
#         This would allow administrators to override default templates
#         with custom HTML/text content stored in the database.
#         
#         Args:
#             template_name: Template identifier (e.g., 'process_failure')
#             format_type: Template format ('html' or 'text')
#             
#         Returns:
#             Optional[str]: Custom template content or None if not found
#         """
#         pass 