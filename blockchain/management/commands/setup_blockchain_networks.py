from django.core.management.base import BaseCommand
from blockchain.models import BlockchainNetwork


class Command(BaseCommand):
    help = 'Setup blockchain networks in the database'

    def handle(self, *args, **options):
        networks = [
            {
                'name': 'Ethereum Mainnet',
                'network_type': 'ethereum',
                'chain_id': 1,
                'rpc_url': 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
                'explorer_url': 'https://etherscan.io',
                'is_testnet': False,
                'is_active': True,
            },
            {
                'name': 'Polygon Mainnet',
                'network_type': 'polygon',
                'chain_id': 137,
                'rpc_url': 'https://polygon-rpc.com',
                'explorer_url': 'https://polygonscan.com',
                'is_testnet': False,
                'is_active': True,
            },
            {
                'name': 'Polygon Mumbai Testnet',
                'network_type': 'polygon_mumbai',
                'chain_id': 80001,
                'rpc_url': 'https://rpc-mumbai.maticvigil.com',
                'explorer_url': 'https://mumbai.polygonscan.com',
                'is_testnet': True,
                'is_active': True,
            },
            {
                'name': 'BSC Mainnet',
                'network_type': 'bsc',
                'chain_id': 56,
                'rpc_url': 'https://bsc-dataseed.binance.org',
                'explorer_url': 'https://bscscan.com',
                'is_testnet': False,
                'is_active': False,  # Not active by default
            },
            {
                'name': 'BSC Testnet',
                'network_type': 'bsc_testnet',
                'chain_id': 97,
                'rpc_url': 'https://data-seed-prebsc-1-s1.binance.org:8545',
                'explorer_url': 'https://testnet.bscscan.com',
                'is_testnet': True,
                'is_active': False,  # Not active by default
            },
        ]

        created_count = 0
        updated_count = 0

        for network_data in networks:
            network, created = BlockchainNetwork.objects.get_or_create(
                chain_id=network_data['chain_id'],
                defaults=network_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created network: {network.name}')
                )
            else:
                # Update existing network
                for key, value in network_data.items():
                    setattr(network, key, value)
                network.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated network: {network.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(networks)} networks. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
