from sorcha_cmdline.sorchaargumentparser import SorchaArgumentParser

#
# sorcha outputs create-sqlite
#


def cmd_outputs_create_sqlite(args):  # pragma: no cover
    #
    # NOTE: DO NOT MOVE THESE IMPORTS TO THE TOP LEVEL OF THE MODULE !!!
    #
    #       Importing sorcha from the function and not at the top-level of the module
    #       allows us to exit quickly and print the help/error message (in case there
    #       was a mistake on the command line). Importing sorcha can take 5 seconds or
    #       more, and making the user wait that long just to print out an erro message
    #       is poor user experience.
    #
    from sorcha.utilities.createResultsSQLDatabase import create_results_database
    from sorcha.utilities.fileAccessUtils import FindDirectoryOrExit
    import os

    args.output = os.path.abspath(args.output)
    args.inputs = os.path.abspath(args.inputs)
    args.results = os.path.abspath(args.results)

    _ = FindDirectoryOrExit(args.inputs, "-i, --inputs")
    _ = FindDirectoryOrExit(args.results, "-r, --results")

    return create_results_database(args)


#
# sorcha outputs check-logs
#


def cmd_outputs_check_logs(args):  # pragma: no cover
    from sorcha.utilities.check_output_logs import check_output_logs
    from sorcha.utilities.fileAccessUtils import FindDirectoryOrExit
    import os

    args.filepath = os.path.abspath(args.filepath)
    _ = FindDirectoryOrExit(args.filepath, "-f, --filepath")

    if args.outpath:
        args.outpath = os.path.abspath(args.outpath)
        _ = FindDirectoryOrExit(os.path.dirname(args.outpath), "-o, --outpath")

        if os.path.exists(args.outpath) and not args.force:
            print(
                "File already found at {}. Re-run with --force argument to overwrite existing output.".format(
                    args.outpath
                )
            )
            return
        elif os.path.exists(args.outpath) and args.force:
            os.remove(args.outpath)

        if args.outpath[-4:] != ".csv":
            args.outpath = args.outpath + ".csv"

    return check_output_logs(args.filepath, args.outpath)


#
# sorcha outputs
#


def main():
    # Create the top-level parser
    parser = SorchaArgumentParser(prog="sorcha outputs", description="Sorcha outputs manipulation utility")
    subparsers = parser.add_subparsers(
        title="commands", description="Available commands", help="Command to execute", dest="command"
    )

    # Add the `create_sqlite` subcommand
    outputs_create_sqlite_parser = subparsers.add_parser(
        "create-sqlite", help="Creating a combined results+inputs SQL database."
    )
    outputs_create_sqlite_parser.set_defaults(func=cmd_outputs_create_sqlite)

    outputs_create_sqlite_parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Filepath and name where you want to save the created SQLite database.",
    )
    outputs_create_sqlite_parser.add_argument(
        "-i",
        "--inputs",
        type=str,
        required=True,
        help="Path location of Sorcha input text files (orbits, physical parameters and config files).",
    )
    outputs_create_sqlite_parser.add_argument(
        "-r",
        "--results",
        type=str,
        required=True,
        help="Path location of Sorcha results files/folders. Code will search subdirectories recursively.",
    )
    outputs_create_sqlite_parser.add_argument(
        "-s",
        "--stem",
        type=str,
        help="Stem filename of Sorcha results files. Used to find Sorcha output filenames. Use if you want to specify.",
    )
    outputs_create_sqlite_parser.add_argument(
        "-c",
        "--complex",
        default=False,
        action="store_true",
        help="Toggle whether to look for complex physical parameters files. Default False.",
    )

    # Add the `check-logs` subcommand
    outputs_create_checklog_parser = subparsers.add_parser(
        "check-logs",
        help="Check all Sorcha log files within a directory and subdirectories for successful/unsuccessful runs.",
    )
    outputs_create_checklog_parser.set_defaults(func=cmd_outputs_check_logs)

    outputs_create_checklog_parser.add_argument(
        "-f",
        "--filepath",
        type=str,
        required=True,
        help="Top level directory in which to search for Sorcha log files. Code will search subdirectories recursively.",
    )
    outputs_create_checklog_parser.add_argument(
        "-o",
        "--outpath",
        type=str,
        default=False,
        help="Output filepath and name to save output .csv, if desired. If not supplied, output will be printed to the terminal.",
    )
    outputs_create_checklog_parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="Force overwrite existing output file. Default is False.",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the appropriate function based on the subcommand
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
