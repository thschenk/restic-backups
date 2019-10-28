#!/usr/bin/python3

import logging
import subprocess
import os
import schedule
import time
from itertools import cycle


from config import config
from contexts import GoogleAuthenticationContext, ResticContext

def cmd_init(options):

    for volume_id in options.volumes:
        logging.info('Initialising volume '+volume_id)

        volume_settings = config.get_volume_settings(volume_id)

        # setup environment contexts
        auth = GoogleAuthenticationContext(volume_id)
        restic = ResticContext(volume_id)

        with auth, restic:
            cmd = [config.global_settings['restic_binary'],
                '--verbose',
                'init'
                ]

            logging.info('>>'+str(cmd))
            subprocess.run(cmd, check=True)
            logging.info('done.')

def single_backup(volume_id):
    logging.info('Backing up volume '+volume_id)

    try:
        volume_settings = config.get_volume_settings(volume_id)

        excludes = volume_settings.get('exclude', [])

        # setup environment contexts
        auth = GoogleAuthenticationContext(volume_id)
        restic = ResticContext(volume_id)

        with auth, restic:
            cmd = [config.global_settings['restic_binary'],
                '--verbose',
                *sum(zip(cycle(['--exclude']), excludes),()),
                'backup',
                volume_settings['local']
                ]

            logging.info('>>'+str(cmd))
            subprocess.run(cmd, check=True)
            logging.info('done.')

    except Exception:
        logging.exception('Something went wrong during backing up of '+volume_id)


def backup_all():
    logging.info('Backing up all volumes...')
    for volume_id in config.all_volume_ids():
        single_backup(volume_id)


def cmd_backup(options):

    volume_ids = options.volumes or config.all_volume_ids()

    logging.info('Volumes to backup: ', ' '.join(volume_ids))
    for volume_id in volume_ids:
        single_backup(volume_id)

def cmd_run(options):
    logging.info('Starting scheduler')

    schedule.every().day.at(options.at).do(backup_all)

    last_next_run = None

    while True:

        next_run = schedule.next_run()
        if next_run != last_next_run:
            last_next_run = next_run
            next_run_str = schedule.next_run().strftime("%c")
            next_run_seconds = schedule.idle_seconds()
            logging.info('Next run is at '+next_run_str+' that is still '+str(next_run_seconds)+' seconds')

        schedule.run_pending()
        time.sleep(1)


if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Backup using restic')
    parser.add_argument('--config', default='config.json')
    parser.add_argument('--cache', default='/cache')
    parser.add_argument('--restic-binary', default='restic')



    subparsers = parser.add_subparsers(dest='command')
    parser_init = subparsers.add_parser('init', help='Initialize backups')
    parser_init.add_argument('volumes', nargs='+')

    parser_backup = subparsers.add_parser('backup', help='Make backups now')
    parser_backup.add_argument('volumes', nargs='*', help='Which sections (empty means all)')

    parser_run = subparsers.add_parser('run', help='Run scheduler')
    parser_run.add_argument('--at', default='02:30')

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    options = parser.parse_args()
    logging.info(options)

    config.global_settings['cache'] = options.cache
    config.global_settings['restic_binary'] = options.restic_binary
    config.load_json_config(options.config)

    if options.command=='backup':
        cmd_backup(options)

    elif options.command=='init':
        cmd_init(options)

    elif options.command=='run':
        cmd_run(options)

    else:
        raise Exception('Unknown action: '+str(options.action))
