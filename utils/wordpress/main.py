
from wordpress_secrets import create_wordpress_secrets
from wordpress_service import create_wordpress_service
from wordpress_deployment import create_wordpress_deployment_with_mysql

if __name__ == "__main__":
    create_wordpress_secrets()
    create_wordpress_deployment_with_mysql()
    create_wordpress_service()
