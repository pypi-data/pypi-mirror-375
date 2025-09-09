import argparse

from sqlalembic.core.project_structure import ProjectStructure


def main():
    parser = argparse.ArgumentParser(description="Sqlalembic Framework Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    startproject_parser = subparsers.add_parser("startproject", help="Create a new project")
    startproject_parser.add_argument("project_name", help="Project name")

    args = parser.parse_args()

    if args.command == "startproject":
        project = ProjectStructure(args.project_name)
        project.startproject()
        print(f"Project '{args.project_name}' created successfully!")
        print(f"Now you can use 'python manage.py <command>' inside your project.")

if __name__ == "__main__":
    main()