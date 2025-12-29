#!/usr/bin/env python3
"""
new-vertical.py - Scaffold a new vertical agent project

Usage:
    python tools/new-vertical.py --name "veterinary-clinics"
    python tools/new-vertical.py --name "auto-repair" --clone "veterinary-clinics"
    python tools/new-vertical.py --name "construction" --discover
"""

import argparse
import os
import shutil
from pathlib import Path
from datetime import date
import re

# Paths
REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = REPO_ROOT / "verticals" / "_template"
VERTICALS_DIR = REPO_ROOT / "verticals"


def slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


def create_vertical(name: str, clone_from: str = None, discover: bool = False):
    """Create a new vertical from template or clone."""
    
    slug = slugify(name)
    target_dir = VERTICALS_DIR / slug
    
    if target_dir.exists():
        print(f"❌ Vertical '{slug}' already exists at {target_dir}")
        return False
    
    # Determine source
    if clone_from:
        source_dir = VERTICALS_DIR / slugify(clone_from)
        if not source_dir.exists():
            print(f"❌ Cannot clone: '{clone_from}' not found")
            return False
        print(f"📋 Cloning from {clone_from}...")
    else:
        source_dir = TEMPLATE_DIR
        print(f"📝 Creating from template...")
    
    # Copy directory
    shutil.copytree(source_dir, target_dir)
    
    # Update VERTICAL.md
    vertical_md = target_dir / "VERTICAL.md"
    if vertical_md.exists():
        content = vertical_md.read_text()
        
        # Replace placeholders
        replacements = {
            "_template": slug,
            "[Industry Name]": name.title(),
            "YYYY-MM-DD": date.today().isoformat(),
            "pending": "research" if discover else "draft",
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        vertical_md.write_text(content)
    
    # Create directory structure
    subdirs = [
        "onboarding",
        "integrations", 
        "marketing",
    ]
    for subdir in subdirs:
        (target_dir / subdir).mkdir(exist_ok=True)
        (target_dir / subdir / ".gitkeep").touch()
    
    print(f"✅ Created vertical: {target_dir}")
    print()
    print("📁 Structure created:")
    print(f"   {target_dir}/")
    print(f"   ├── VERTICAL.md          # Fill this out first")
    print(f"   ├── persona.md           # Generate with Prometheus")
    print(f"   ├── onboarding/          # Intake flow definitions")
    print(f"   ├── integrations/        # Tool configs")
    print(f"   └── marketing/           # Landing page, pitch deck")
    print()
    
    if discover:
        print("🔍 Discovery mode enabled. Next steps:")
        print("   1. Run: python tools/research-vertical.py --name", f'"{name}"')
        print("   2. Review generated VERTICAL.md")
        print("   3. Run: python tools/generate-persona.py", f"verticals/{slug}/VERTICAL.md")
    else:
        print("📝 Next steps:")
        print(f"   1. Edit verticals/{slug}/VERTICAL.md")
        print(f"   2. Run: python tools/generate-persona.py verticals/{slug}/VERTICAL.md")
        print(f"   3. Define onboarding flow in verticals/{slug}/onboarding/")
    
    return True


def list_verticals():
    """List all existing verticals."""
    print("📂 Existing verticals:")
    print()
    
    for item in sorted(VERTICALS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith('_'):
            vertical_md = item / "VERTICAL.md"
            status = "unknown"
            
            if vertical_md.exists():
                content = vertical_md.read_text()
                if "status: research" in content:
                    status = "🔍 research"
                elif "status: draft" in content:
                    status = "📝 draft"
                elif "status: building" in content:
                    status = "🔨 building"
                elif "status: pilot" in content:
                    status = "🧪 pilot"
                elif "status: live" in content:
                    status = "✅ live"
            
            print(f"   {item.name:<25} {status}")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new vertical agent project"
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Name of the new vertical (e.g., 'veterinary clinics')"
    )
    parser.add_argument(
        "--clone", "-c",
        type=str,
        help="Clone from an existing vertical instead of template"
    )
    parser.add_argument(
        "--discover", "-d",
        action="store_true",
        help="Enable discovery mode (triggers research agent)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List existing verticals"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_verticals()
        return
    
    if not args.name:
        parser.print_help()
        print()
        print("Example:")
        print('  python tools/new-vertical.py --name "veterinary clinics"')
        print('  python tools/new-vertical.py --name "auto repair" --discover')
        print('  python tools/new-vertical.py --list')
        return
    
    create_vertical(args.name, args.clone, args.discover)


if __name__ == "__main__":
    main()
