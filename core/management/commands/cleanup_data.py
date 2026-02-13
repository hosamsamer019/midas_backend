"""
Management command to clean up and normalize database data.
This command identifies and merges duplicate bacteria and antibiotic entries.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.master_data import master_data_manager
from core.data_normalization import identify_duplicates
import json


class Command(BaseCommand):
    help = 'Clean up and normalize database data (bacteria and antibiotics)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--auto-merge',
            action='store_true',
            help='Automatically merge duplicates without confirmation',
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='Only generate a report of duplicates without merging',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file for the cleanup report (JSON format)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Data Cleanup and Normalization Tool'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        dry_run = options['dry_run']
        auto_merge = options['auto_merge']
        report_only = options['report_only']
        output_file = options['output']

        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be made'))
            self.stdout.write('')

        # Step 1: Identify bacteria duplicates
        self.stdout.write(self.style.HTTP_INFO('Step 1: Identifying bacteria duplicates...'))
        bacteria_duplicates = master_data_manager.identify_bacteria_duplicates()
        
        if bacteria_duplicates:
            self.stdout.write(self.style.WARNING(f'Found {len(bacteria_duplicates)} bacteria with duplicates:'))
            for normalized_name, variations in bacteria_duplicates.items():
                self.stdout.write(f'  • {normalized_name}:')
                for variation in variations:
                    self.stdout.write(f'    - {variation}')
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No bacteria duplicates found'))
        
        self.stdout.write('')

        # Step 2: Identify antibiotic duplicates
        self.stdout.write(self.style.HTTP_INFO('Step 2: Identifying antibiotic duplicates...'))
        antibiotic_duplicates = master_data_manager.identify_antibiotic_duplicates()
        
        if antibiotic_duplicates:
            self.stdout.write(self.style.WARNING(f'Found {len(antibiotic_duplicates)} antibiotics with duplicates:'))
            for normalized_name, variations in antibiotic_duplicates.items():
                self.stdout.write(f'  • {normalized_name}:')
                for variation in variations:
                    self.stdout.write(f'    - {variation}')
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ No antibiotic duplicates found'))
        
        self.stdout.write('')

        # Generate report
        report = {
            'bacteria_duplicates': bacteria_duplicates,
            'antibiotic_duplicates': antibiotic_duplicates,
            'total_bacteria_duplicates': len(bacteria_duplicates),
            'total_antibiotic_duplicates': len(antibiotic_duplicates),
            'actions_taken': []
        }

        # If report-only, save and exit
        if report_only:
            self.stdout.write(self.style.HTTP_INFO('Report-only mode - no merging will be performed'))
            if output_file:
                self._save_report(report, output_file)
            return

        # Step 3: Merge bacteria duplicates
        if bacteria_duplicates and not dry_run:
            self.stdout.write(self.style.HTTP_INFO('Step 3: Merging bacteria duplicates...'))
            
            for normalized_name, variations in bacteria_duplicates.items():
                if len(variations) <= 1:
                    continue
                
                # Use the first variation as the canonical name
                keep_name = variations[0]
                merge_names = variations[1:]
                
                if not auto_merge:
                    self.stdout.write(f'\nMerge bacteria variations into "{keep_name}"?')
                    for name in merge_names:
                        self.stdout.write(f'  - {name}')
                    
                    response = input('Proceed? (y/n): ')
                    if response.lower() != 'y':
                        self.stdout.write(self.style.WARNING('  Skipped'))
                        continue
                
                try:
                    samples_updated, bacteria_deleted = master_data_manager.merge_bacteria_duplicates(
                        keep_name, merge_names
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Merged {bacteria_deleted} bacteria, updated {samples_updated} samples'
                    ))
                    
                    report['actions_taken'].append({
                        'type': 'bacteria_merge',
                        'keep_name': keep_name,
                        'merged_names': merge_names,
                        'samples_updated': samples_updated,
                        'bacteria_deleted': bacteria_deleted
                    })
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                    report['actions_taken'].append({
                        'type': 'bacteria_merge_error',
                        'keep_name': keep_name,
                        'merged_names': merge_names,
                        'error': str(e)
                    })
            
            self.stdout.write('')

        # Step 4: Merge antibiotic duplicates
        if antibiotic_duplicates and not dry_run:
            self.stdout.write(self.style.HTTP_INFO('Step 4: Merging antibiotic duplicates...'))
            
            for normalized_name, variations in antibiotic_duplicates.items():
                if len(variations) <= 1:
                    continue
                
                # Use the first variation as the canonical name
                keep_name = variations[0]
                merge_names = variations[1:]
                
                if not auto_merge:
                    self.stdout.write(f'\nMerge antibiotic variations into "{keep_name}"?')
                    for name in merge_names:
                        self.stdout.write(f'  - {name}')
                    
                    response = input('Proceed? (y/n): ')
                    if response.lower() != 'y':
                        self.stdout.write(self.style.WARNING('  Skipped'))
                        continue
                
                try:
                    results_updated, antibiotics_deleted = master_data_manager.merge_antibiotic_duplicates(
                        keep_name, merge_names
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Merged {antibiotics_deleted} antibiotics, updated {results_updated} test results'
                    ))
                    
                    report['actions_taken'].append({
                        'type': 'antibiotic_merge',
                        'keep_name': keep_name,
                        'merged_names': merge_names,
                        'results_updated': results_updated,
                        'antibiotics_deleted': antibiotics_deleted
                    })
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                    report['actions_taken'].append({
                        'type': 'antibiotic_merge_error',
                        'keep_name': keep_name,
                        'merged_names': merge_names,
                        'error': str(e)
                    })
            
            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Cleanup Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Bacteria duplicates found: {len(bacteria_duplicates)}')
        self.stdout.write(f'Antibiotic duplicates found: {len(antibiotic_duplicates)}')
        
        if not dry_run and not report_only:
            self.stdout.write(f'Actions taken: {len(report["actions_taken"])}')
        
        self.stdout.write('')

        # Save report if requested
        if output_file:
            self._save_report(report, output_file)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN completed - no changes were made'))
        elif report_only:
            self.stdout.write(self.style.HTTP_INFO('Report generated successfully'))
        else:
            self.stdout.write(self.style.SUCCESS('Cleanup completed successfully!'))

    def _save_report(self, report, output_file):
        """Save the cleanup report to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f'Report saved to: {output_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to save report: {str(e)}'))
