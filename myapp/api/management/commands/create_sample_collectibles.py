from django.core.management.base import BaseCommand
from myapp.api.models import CollectibleItem
from django.utils import timezone


class Command(BaseCommand):
    help = 'Creates sample collectible items for testing'

    def handle(self, *args, **options):
        # Create sample items only if none exist
        if CollectibleItem.objects.count() == 0:
            self.stdout.write('Creating sample collectible items...')
            
            # Common Circuit Designs
            CollectibleItem.objects.create(
                name='Basic Circuit Design',
                description='A simple circuit design blueprint for beginners.',
                image_url='https://placehold.co/400x400?text=Basic+Circuit',
                rarity='common',
                type='badge'
            )
            
            CollectibleItem.objects.create(
                name='LED Flasher Circuit',
                description='A basic LED circuit that flashes at regular intervals.',
                image_url='https://placehold.co/400x400?text=LED+Circuit',
                rarity='common',
                type='badge'
            )
            
            # Rare Circuit Designs
            CollectibleItem.objects.create(
                name='Timer Circuit',
                description='A 555 timer circuit with adjustable timing.',
                image_url='https://placehold.co/400x400?text=Timer+Circuit',
                rarity='rare',
                type='badge'
            )
            
            CollectibleItem.objects.create(
                name='Audio Amplifier',
                description='A clean audio amplifier circuit design.',
                image_url='https://placehold.co/400x400?text=Audio+Amp',
                rarity='rare',
                type='badge'
            )
            
            # Epic Circuit Designs
            CollectibleItem.objects.create(
                name='Microcontroller Board',
                description='A custom microcontroller board with multiple I/O options.',
                image_url='https://placehold.co/400x400?text=Microcontroller',
                rarity='epic',
                type='badge'
            )
            
            CollectibleItem.objects.create(
                name='Wireless Transmitter',
                description='A long-range wireless communication circuit.',
                image_url='https://placehold.co/400x400?text=Wireless',
                rarity='epic',
                type='badge'
            )
            
            # Legendary Circuit Designs
            CollectibleItem.objects.create(
                name='Quantum Circuit',
                description='A theoretical quantum computing circuit design.',
                image_url='https://placehold.co/400x400?text=Quantum',
                rarity='legendary',
                type='badge'
            )
            
            CollectibleItem.objects.create(
                name='Neural Interface',
                description='An advanced brain-computer interface circuit.',
                image_url='https://placehold.co/400x400?text=Neural',
                rarity='legendary',
                type='badge'
            )
            
            # Create some profile icons/frames too
            CollectibleItem.objects.create(
                name='Circuit Board Frame',
                description='A profile frame designed like a circuit board.',
                image_url='https://placehold.co/400x400?text=Circuit+Frame',
                rarity='rare',
                type='frame'
            )
            
            CollectibleItem.objects.create(
                name='Engineer Icon',
                description='A profile icon for engineers.',
                image_url='https://placehold.co/400x400?text=Engineer+Icon',
                rarity='epic',
                type='icon'
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully created sample collectible items'))
        else:
            self.stdout.write(self.style.WARNING('Collectible items already exist - skipping creation')) 