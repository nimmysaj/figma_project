try:
    import rest_framework
    print("Django REST Framework is installed.")
except ImportError as e:
    print("Error:", e)
