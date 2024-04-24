import subprocess


def print_instructions():
    print("Instructions for setting up and running Polarion.py:")

    print("\n1. Install necessary packages:")
    inputted = input("   \u21AA  Do you want to install the necessary packages? (y/n): ")
    if inputted.lower() == 'y':
        print("Installing packages...")
        subprocess.run(["start", "/wait", "cmd", "pip install -r requirements.txt"], shell=True)
        print("Packages installed.")
    else:
        print("   Ensure all necessary packages are installed before running the script.")

    print("\n2. Run the Cloud GPU:")
    print("   - Open your browser and navigate to the following link: https://marketplace.tensordock.com/deploy")
    print("   - Follow the instruction made by Luca Abs for the deployment of the cloud GPU via TensorDock.")
    print("     \u21AA Note : Automation of this process is possible but not implemented.")


print_instructions()
input("\nPress Enter when these instructions have been completed.")
