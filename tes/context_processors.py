def theme_colors(request):
    """
    Context processor to provide primary, secondary and background colors.
    Colors are hardcoded to ensure a consistent theme for all users.
    """
    return {
        'primary_color': '#004f00',
        'secondary_color': '#00591c',
        'background_color': '#deffea',
    }
