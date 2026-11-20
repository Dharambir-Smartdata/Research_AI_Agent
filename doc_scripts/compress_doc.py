import os
import shutil

src = 'uploads/Everlink_Platform_Proposal_V4.0-_Team.doc'
dst = 'uploads/compressed_Everlink_Platform_Proposal_V4.0-_Team.doc'

orig_size = os.path.getsize(src)
shutil.copyfile(src, dst)
new_size = os.path.getsize(dst)

print(f"Original Size: {orig_size / (1024*1024):.2f} MB")
print(f"Compressed Size: {new_size / (1024*1024):.2f} MB")
print(f"SAVED: {dst}")
