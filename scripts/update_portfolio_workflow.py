#!/usr/bin/env python
"""
Automated workflow script for adding new portfolio images.

This script:
1. Runs AI analysis on new images in assets/photos
2. Copies the latest analysis data to the website
3. Starts the dev server for testing
4. Builds and deploys if approved
5. Pushes changes to both git repositories
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Paths
PARENT_DIR = Path("/Users/chaitanyamalhotra/Desktop/scratch projects/carpenter portfolio")
WEBSITE_DIR = PARENT_DIR / "portfolio-website"
ASSETS_DIR = PARENT_DIR / "assets" / "photos"
SCRIPTS_DIR = PARENT_DIR / "scripts"
ANALYSIS_JSON = PARENT_DIR / "data" / "raw" / "image_analysis_results.json"
WEBSITE_JSON = WEBSITE_DIR / "public" / "image_analysis_results.json"


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")


def print_step(num, total, title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{num}/{total}] {title}{Colors.RESET}")
    print("-" * 60)


def run_command(cmd, cwd=None, description=""):
    """Run a shell command and return success status."""
    if description:
        print_info(f"Running: {description}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            if description and "--quiet" not in cmd:
                print_success("Done")
            return True, result.stdout
        else:
            print_error(f"Failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False, str(e)


def check_for_new_images():
    """Check if there are new images to analyze."""
    print_step(1, 7, "Checking for new images in assets/photos")

    if not ASSETS_DIR.exists():
        print_error(f"Assets directory not found: {ASSETS_DIR}")
        return False

    # Check if analysis exists
    if not ANALYSIS_JSON.exists():
        print_info("No existing analysis found. All images will be processed.")
        return True

    # Get list of images
    image_files = list(ASSETS_DIR.glob("*.*"))
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    image_files = [f for f in image_files if f.suffix.lower() in image_extensions]

    if not image_files:
        print_warning("No images found in assets/photos")
        return False

    print_info(f"Found {len(image_files)} images in assets/photos")
    return True


def run_image_analysis():
    """Run the AI image analysis script."""
    print_step(2, 7, "Running AI image analysis")

    analysis_script = SCRIPTS_DIR / "continue_image_analysis.py"

    if not analysis_script.exists():
        print_error(f"Analysis script not found: {analysis_script}")
        return False

    success, _ = run_command(
        f'python "{analysis_script}"',
        cwd=PARENT_DIR
    )

    return success


def copy_images_to_website():
    """Copy new images to the website public/images directory."""
    print_step(3, 7, "Copying images to website")

    website_images_dir = WEBSITE_DIR / "public" / "images"

    if not website_images_dir.exists():
        print_error(f"Website images directory not found: {website_images_dir}")
        return False

    # Get all images from assets
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    image_files = list(ASSETS_DIR.glob("*.*"))
    image_files = [f for f in image_files if f.suffix.lower() in image_extensions]

    copied = 0
    for image_file in image_files:
        dest = website_images_dir / image_file.name
        if not dest.exists():
            subprocess.run(['cp', str(image_file), str(dest)])
            copied += 1
            print(f"  Copied: {image_file.name}")

    if copied > 0:
        print_success(f"Copied {copied} new images")
    else:
        print_info("All images already exist (no new copies needed)")

    return True


def update_analysis_data():
    """Copy the latest analysis data to the website."""
    print_step(4, 7, "Updating analysis data in website")

    if not ANALYSIS_JSON.exists():
        print_error(f"Analysis data not found: {ANALYSIS_JSON}")
        return False

    success, _ = run_command(
        f'cp "{ANALYSIS_JSON}" "{WEBSITE_JSON}"'
    )

    return success


def start_dev_server():
    """Start the development server for testing."""
    print_step(5, 7, "Starting development server")
    print_info(f"Server will run at: http://localhost:5173/")
    print_warning("Press Ctrl+C when you're done testing")
    print_info("Waiting for you to test the changes...")

    # Change to website directory
    os.chdir(WEBSITE_DIR)

    try:
        # Start dev server
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print_info("\nDev server stopped by user")
        return True
    except Exception as e:
        print_error(f"Failed to start dev server: {e}")
        return False


def build_and_deploy():
    """Build the website and deploy to Cloudflare Pages."""
    print_step(7, 7, "Building and deploying website")

    # Build
    print_info("Building website...")
    success, _ = run_command(
        "npm run build",
        cwd=WEBSITE_DIR
    )

    if not success:
        return False

    # Deploy
    print_info("Deploying to Cloudflare Pages...")
    success, _ = run_command(
        "npx wrangler pages deploy dist",
        cwd=WEBSITE_DIR
    )

    return success


def commit_and_push_repos():
    """Commit and push changes to both git repositories."""
    print_step(6, 7, "Committing and pushing to git repositories")

    # Commit and push website repo
    print_info("Website repository...")

    os.chdir(WEBSITE_DIR)
    run_command("git add -A", cwd=WEBSITE_DIR, description="Staging changes")
    run_command('git commit -m "Update portfolio with new images and analysis data"', cwd=WEBSITE_DIR, description="Committing changes")
    run_command("git push", cwd=WEBSITE_DIR, description="Pushing to GitHub")

    # Commit and push parent repo
    print_info("Parent repository...")

    os.chdir(PARENT_DIR)
    run_command("git add -A", cwd=PARENT_DIR, description="Staging changes")
    run_command('git commit -m "Update analysis data for new portfolio images"', cwd=PARENT_DIR, description="Committing changes")
    run_command("git push", cwd=PARENT_DIR, description="Pushing to GitHub")

    return True


def main():
    """Main workflow function."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== Sher Mohammad Portfolio - Image Update Workflow ==={Colors.RESET}\n")

    steps = [
        check_for_new_images,
        run_image_analysis,
        copy_images_to_website,
        update_analysis_data,
        start_dev_server,
        commit_and_push_repos,
        build_and_deploy
    ]

    for i, step in enumerate(steps, 1):
        try:
            success = step()

            if not success:
                print_error(f"Step {i} failed. Aborting workflow.")
                sys.exit(1)

        except Exception as e:
            print_error(f"Step {i} encountered an error: {str(e)}")
            sys.exit(1)

    print(f"\n{Colors.GREEN}{Colors.BOLD}=== Workflow Complete! ==={Colors.RESET}")
    print_success("All tasks completed successfully!")
    print_info("Your portfolio has been updated and deployed.")
    print_info(f"Live site: https://sher-mohammad-carpenter.pages.dev")


if __name__ == "__main__":
    main()
