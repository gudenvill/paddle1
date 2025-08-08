#!/usr/bin/env python3
"""
Rename all files in input directory to numbered sequence (1.png, 2.png, etc.)
"""

import os
import shutil
from pathlib import Path

def rename_input_files():
    """
    Rename all files in input/ directory to numbered sequence.
    """
    
    input_dir = "input"
    
    if not os.path.exists(input_dir):
        print(f"❌ Directory {input_dir}/ not found!")
        return
    
    # Get all files in input directory
    files = []
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path):
            files.append(file)
    
    # Sort files by name to maintain some order
    files.sort()
    
    print(f"📁 Found {len(files)} files in {input_dir}/")
    print("🔄 Starting rename process...")
    print("=" * 50)
    
    # Track renames
    renamed_count = 0
    skipped_count = 0
    
    # Create backup list of original names
    rename_log = []
    
    for i, original_name in enumerate(files, 1):
        original_path = os.path.join(input_dir, original_name)
        
        # Get file extension
        file_ext = Path(original_name).suffix.lower()
        if not file_ext:
            file_ext = '.png'  # Default to png if no extension
        
        # New numbered name
        new_name = f"{i}{file_ext}"
        new_path = os.path.join(input_dir, new_name)
        
        # Skip if it's already the target name
        if original_name == new_name:
            print(f"⏩ Skip: {original_name} (already correct)")
            skipped_count += 1
            continue
        
        # Check if target already exists (to avoid conflicts)
        if os.path.exists(new_path):
            # Move existing target to temporary name first
            temp_name = f"temp_{i}_{new_name}"
            temp_path = os.path.join(input_dir, temp_name)
            print(f"⚠️  Conflict: {new_name} exists, using temporary name")
            new_name = temp_name
            new_path = temp_path
        
        try:
            # Rename the file
            shutil.move(original_path, new_path)
            print(f"✅ {original_name} → {new_name}")
            
            rename_log.append({
                "original": original_name,
                "new": new_name,
                "number": i
            })
            renamed_count += 1
            
        except Exception as e:
            print(f"❌ Error renaming {original_name}: {str(e)}")
    
    print("=" * 50)
    print(f"📊 RENAME SUMMARY:")
    print(f"   • Total files found: {len(files)}")
    print(f"   • Successfully renamed: {renamed_count}")
    print(f"   • Skipped (already correct): {skipped_count}")
    print(f"   • Files now numbered: 1{Path(files[0]).suffix} to {len(files)}{Path(files[-1]).suffix}")
    
    # Save rename log
    if rename_log:
        log_file = "rename_log.txt"
        with open(log_file, 'w') as f:
            f.write("Original Name → New Name\n")
            f.write("=" * 40 + "\n")
            for entry in rename_log:
                f.write(f"{entry['original']} → {entry['new']}\n")
        
        print(f"   • Rename log saved: {log_file}")
    
    print("\n🎉 Rename process completed!")
    
    # Show final file list
    print("\n📋 Final file list:")
    final_files = sorted(os.listdir(input_dir))
    for i, file in enumerate(final_files[:10], 1):  # Show first 10
        print(f"   {i:2d}. {file}")
    
    if len(final_files) > 10:
        print(f"   ... and {len(final_files) - 10} more files")

if __name__ == "__main__":
    print("🔄 Input File Renamer - Converting to Numbered Sequence")
    print()
    
    # Ask for confirmation
    response = input("⚠️  This will rename ALL files in input/ directory. Continue? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        rename_input_files()
    else:
        print("❌ Rename cancelled.") 