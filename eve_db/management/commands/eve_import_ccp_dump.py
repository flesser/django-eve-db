import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS
from eve_db.ccp_importer import util
from eve_db.ccp_importer import importers

def exit_with_error(error_msg):
    """
    Gracefully kills the script when an error was occured.
    """
    print error_msg
    sys.exit(1)

def exit_with_succ():
    """
    Nothing to see here, move along.
    """
    sys.exit(0)

def list_tables(option, opt, value, parser):
    """
    Prints a list of tables that are available for import.
    """
    print "CCP Data Dump Table List"
    print "------------------------"
    for table in util.IMPORT_LIST:
        print "%s" % table.__name__.replace('Importer_', '')
    print "-- %d tables --" % len(util.IMPORT_LIST)
    # The -l argument is just used for listing, proceed no further.
    exit_with_succ()

def check_for_eve_db(sqlite_file):
    """
    Checks for the presence of the CCP EVE dump in SQLite format. Exit if
    this can't be found.
    """
    try:
        dbfile = open(sqlite_file, 'r')
    except IOError:
        exit_with_error("""No CCP data dump could be found. Visit 
http://wiki.eve-id.net/CCP_Database_Dump_Resources#Conversions
and download the latest SQLite conversion. Copy the SQLite .db file to the 
same directory as your settings.py file and re-name it to ccp_dump.db. You 
should then be able to run this command without issue.""")

def get_importer_classes_from_arg_list(arg_list):
    """
    Validates the user input for tables to import against the importer list.
    Returns a list of importer classes. In the event that one of the
    arguments does not match up against an importer class, raise an
    exception so the user may be notified.
    """
    importer_classes = set()
    for arg in arg_list[1:]:
        importer_class = getattr(importers, 'Importer_%s' % arg, False)
        if importer_class not in util.IMPORT_LIST:
            exit_with_error("No such table to import: %s\n\rNOTE: Table names are case-sensitive." % arg)
        else:
            importer_classes.add(importer_class)
    return importer_classes

def get_importers_for_start_at_import(specified_importers):
    """
    This function replaces the user-specified importer list (which should only
    be one importer to start at), replacing it with the specified importer
    and every importer in the master util.IMPORT_LIST that is sequentially
    after the specified importer.
    """
    importer = list(specified_importers)[0]
    importer_index = util.IMPORT_LIST.index(importer)
    specified_importers = util.IMPORT_LIST[importer_index:]
    return specified_importers

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option("-i", "--include-deps", action="store_true",
                          dest="include_deps", default=False,
                          help="""Import the other tables that the specified table 
                                  [recursively] depends on."""),
        make_option("-l", "--list", action="callback",
                          callback=list_tables,
                          help="List all of the tables in the CCP dump and exit."),
        make_option("-s", "--start-at", action="store_true",
                          dest="start_at_import",
                          help="""Starts and continues the import process at
                                  the specified table."""),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to synchronize. '
                'Defaults to the "default" database.'),
    )
    help = """This importer script will either import one or all tables from
the CCP data dump. If no arguments are specified, all tables will be imported."""
    args = '[table_name1] [table_name2] [...]'

    requires_model_validation = False

    def handle(self, *args, **options):
        """
        This is where the user input is handled, and the appropriate
        actions are taken.
        """
        #print "OPTIONS", options
        #print "ARGS:", args

        if len(args) < 1:
            raise CommandError(
                "You must specify the static data dump file to import. This is "
                "probably something in the pattern of *.db3")

        try:
            sqlite_file = args[0]
            check_for_eve_db(sqlite_file)

            database = options.get('database')
            if database:
                print "Using database '%s'" % database

            if len(args) is 1:
                print "No table names specified, importing all."
                util.run_importers(util.IMPORT_LIST, sqlite_file, database=database)
            else:
                specified_importers = get_importer_classes_from_arg_list(args)
                start_at_import = options.get('start_at_import')
                print "Importing: %s" % args[1:]

                include_deps = options.get('include_deps')
                if include_deps and not start_at_import:
                    print "Including dependencies."

                if start_at_import:
                    # User wishes to start the import process at a specific
                    # table name. Import the specified importer, and
                    # everything after it.
                    specified_importers = get_importers_for_start_at_import(specified_importers)

                util.run_importers(specified_importers, sqlite_file,
                                   include_deps=include_deps, database=database)
        except KeyboardInterrupt:
            print "Terminating early..."
            exit_with_succ()
