from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.scraping.models import (
    ScrapingTarget, ScrapingRule
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up example scraping targets and rules for the scraping app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-examples',
            action='store_true',
            help='Create example scraping targets and rules',
        )
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Create a test user for scraping targets',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create both examples and user',
        )

    def handle(self, *args, **options):
        if options['all'] or options['create_user']:
            self.create_test_user()
        
        if options['all'] or options['create_examples']:
            self.create_example_targets()
        
        if not any([options['create_examples'], options['create_user'], options['all']]):
            self.stdout.write(
                self.style.WARNING(
                    'No action specified. Use --create-examples, --create-user, or --all'
                )
            )

    def create_test_user(self):
        """Create a test user for scraping targets"""
        self.stdout.write('Creating test user...')
        try:
            user, created = User.objects.get_or_create(
                username='scraper_user',
                defaults={
                    'email': 'scraper@example.com',
                    'first_name': 'Scraper',
                    'last_name': 'User',
                    'is_staff': True,
                }
            )
            
            if created:
                user.set_password('scraper123')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created test user: {user.username} (password: scraper123)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Test user {user.username} already exists')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test user: {e}')
            )

    def create_example_targets(self):
        """Create example scraping targets and rules"""
        self.stdout.write('Creating example scraping targets...')
        
        try:
            # Get or create test user
            user = User.objects.get(username='scraper_user')
            
            # Example 1: News website
            news_target, created = ScrapingTarget.objects.get_or_create(
                name='Example News Site',
                defaults={
                    'url': 'https://httpbin.org/html',
                    'status': ScrapingTarget.ScrapingStatus.ACTIVE,
                    'frequency': ScrapingTarget.ScrapingFrequency.HOURLY,
                    'delay_between_requests': 5,
                    'max_requests_per_hour': 50,
                    'respect_robots_txt': True,
                    'user_agent': 'happenin News Scraper (+https://happenin.com/bot)',
                    'created_by': user,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created news target: {news_target.name}')
                
                # Create rules for news site
                self.create_news_rules(news_target)
            else:
                self.stdout.write(f'  - News target already exists: {news_target.name}')
            
            # Example 2: E-commerce site
            ecommerce_target, created = ScrapingTarget.objects.get_or_create(
                name='Example E-commerce Site',
                defaults={
                    'url': 'https://httpbin.org/json',
                    'status': ScrapingTarget.ScrapingStatus.ACTIVE,
                    'frequency': ScrapingTarget.ScrapingFrequency.DAILY,
                    'delay_between_requests': 10,
                    'max_requests_per_hour': 30,
                    'respect_robots_txt': True,
                    'user_agent': 'happenin E-commerce Scraper (+https://happenin.com/bot)',
                    'created_by': user,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created e-commerce target: {ecommerce_target.name}')
                
                # Create rules for e-commerce site
                self.create_ecommerce_rules(ecommerce_target)
            else:
                self.stdout.write(f'  - E-commerce target already exists: {ecommerce_target.name}')
            
            # Example 3: Blog site
            blog_target, created = ScrapingTarget.objects.get_or_create(
                name='Example Blog Site',
                defaults={
                    'url': 'https://httpbin.org/xml',
                    'status': ScrapingTarget.ScrapingStatus.ACTIVE,
                    'frequency': ScrapingTarget.ScrapingFrequency.WEEKLY,
                    'delay_between_requests': 15,
                    'max_requests_per_hour': 20,
                    'respect_robots_txt': True,
                    'user_agent': 'happenin Blog Scraper (+https://happenin.com/bot)',
                    'created_by': user,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created blog target: {blog_target.name}')
                
                # Create rules for blog site
                self.create_blog_rules(blog_target)
            else:
                self.stdout.write(f'  - Blog target already exists: {blog_target.name}')
            
            self.stdout.write(
                self.style.SUCCESS('Example scraping targets created successfully!')
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    'Test user not found. Run with --create-user first.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating example targets: {e}')
            )

    def create_news_rules(self, target):
        """Create scraping rules for news site"""
        rules_data = [
            {
                'name': 'article_title',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': 'h1, .article-title, .headline',
                'data_type': 'text',
                'priority': 1,
                'is_active': True,
            },
            {
                'name': 'article_content',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.article-content, .post-content, .story-body',
                'data_type': 'text',
                'priority': 2,
                'is_active': True,
            },
            {
                'name': 'publish_date',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.publish-date, .article-date, time[datetime]',
                'data_type': 'date',
                'priority': 3,
                'is_active': True,
            },
            {
                'name': 'author_name',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.author, .byline, .writer',
                'data_type': 'text',
                'priority': 4,
                'is_active': True,
            },
        ]
        
        for rule_data in rules_data:
            ScrapingRule.objects.get_or_create(
                target=target,
                name=rule_data['name'],
                defaults=rule_data
            )

    def create_ecommerce_rules(self, target):
        """Create scraping rules for e-commerce site"""
        rules_data = [
            {
                'name': 'product_name',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.product-name, .item-title, h1.product',
                'data_type': 'text',
                'priority': 1,
                'is_active': True,
            },
            {
                'name': 'product_price',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.price, .cost, .amount',
                'data_type': 'number',
                'priority': 2,
                'is_active': True,
            },
            {
                'name': 'product_description',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.description, .product-details, .summary',
                'data_type': 'text',
                'priority': 3,
                'is_active': True,
            },
            {
                'name': 'product_image',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.product-image img, .item-photo img',
                'attribute': 'src',
                'data_type': 'url',
                'priority': 4,
                'is_active': True,
            },
        ]
        
        for rule_data in rules_data:
            ScrapingRule.objects.get_or_create(
                target=target,
                name=rule_data['name'],
                defaults=rule_data
            )

    def create_blog_rules(self, target):
        """Create scraping rules for blog site"""
        rules_data = [
            {
                'name': 'post_title',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.post-title, .entry-title, h1',
                'data_type': 'text',
                'priority': 1,
                'is_active': True,
            },
            {
                'name': 'post_content',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.post-content, .entry-content, .content',
                'data_type': 'text',
                'priority': 2,
                'is_active': True,
            },
            {
                'name': 'post_date',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.post-date, .entry-date, .published',
                'data_type': 'date',
                'priority': 3,
                'is_active': True,
            },
            {
                'name': 'post_author',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.post-author, .entry-author, .author',
                'data_type': 'text',
                'priority': 4,
                'is_active': True,
            },
            {
                'name': 'post_tags',
                'rule_type': ScrapingRule.RuleType.CSS_SELECTOR,
                'selector': '.post-tags, .entry-tags, .tags a',
                'data_type': 'text',
                'priority': 5,
                'is_active': True,
            },
        ]
        
        for rule_data in rules_data:
            ScrapingRule.objects.get_or_create(
                target=target,
                name=rule_data['name'],
                defaults=rule_data
            )
