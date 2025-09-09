"""
Template sample URLs configuration.

This module contains the mapping of template names to their sample image URLs.
Add your S3 URLs here as they become available.
"""

# Template name to S3 URL mapping
TEMPLATE_SAMPLE_URLS = {
    "education_info_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/education_info_2.png",
    "coming_soon_post_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon_post_2.png",
    "quote_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/quote_template.png",
    "calendar_app_promo": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/calendar_app_promo.png",
    "product_service": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_service.png",
    "product_showcase_5": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesproduct_showcase_5.png",
    "product_showcase_4": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase_4.png",
    "product_promotion": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_promotion.png",
    "product_showcase_3": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_showcase_3.png",
    "coming_soon_page": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon_page.png",
    "hiring_post": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/hiring_post.png",
    "education_info": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/education_info.png",
    "product_service_minimal": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/product_service_minimal.png",
    "qa_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/qa_template.png",
    "coming_soon": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/coming_soon.png",
    "brand_info": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesbrand_info.png",
    "product_marketing": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesproduct_marketing.png",
    "brand_info_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesbrand_info_2.png",
    "sale_alert": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatessale_alert.png",
    "testimonials": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatestestimonials.png",
    "event_alert": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesevent_alert.png",
    "product_sale_2": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesproduct_sale_2.png",
    "product_feature": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesproduct_feature.png",
    "event_announcement": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templates/baseevent_announcement.png",
    "super_king_burgers_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatessuper_king_burgers_template.png",
    "shoe_ad_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesshoe_ad_template.png",
    "grilled_chicken_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesgrilled_chicken_template.png",
    "healthy_food_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templateshealthy_food_template.png",
    "product_poster": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesproduct_poster.png",
    "orchid_baby_post": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesorchid_baby_post.png",
    "shelf_engine_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesshelf_engine_template.png",
    "learn_gif_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templateslearn_gif_template.png",
    "sales_offer_poster": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesjuice_poster.png",
    "stamped_loyalty_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesstamped_loyalty_template.png",
    "food_offer_promo": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesfood_offer_promo.png",
    "product_promotion_6": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesbaby_product_promotion.png",
    "food_menu_promo": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesfood_menu_promo.png",
    "reward_program_template": "https://dolze-templates-uat.s3.eu-north-1.amazonaws.com/uploads/templatesreward_program_template.png",
    "social_media_tips_template": "https://i.ibb.co/gMv015G3/social-media-tips-template.png",
    "spotlight_launching": "https://i.ibb.co/rGVRbWJN/Black-White-Modern-Launching-Soon-Instagram-Post.png",
    "faq_template": "https://i.ibb.co/ZpSCsQFB/faq-template.png",
    "neon_creative_agency":"https://i.ibb.co/SDL3bJ58/neon-creative-agency.png"
}


def get_sample_url(template_name: str) -> str:
    """
    Get the sample URL for a template.

    Args:
        template_name: Name of the template

    Returns:
        str: The sample URL if exists, empty string otherwise
    """
    return TEMPLATE_SAMPLE_URLS.get(template_name, "")
