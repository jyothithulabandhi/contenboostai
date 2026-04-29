import db
rows = db.get_history(10)
if rows:
    for r in rows:
        best = "[BEST]" if r["is_best"] else ""
        title = r["generated_title"][:60]
        print(f"ID:{r['id']} | {r['product_name']} | {r['variant_type'].upper()} | Score:{r['seo_score']} {best}")
        print(f"  Title: {title}")
        print()
else:
    print("No saved optimizations yet. Click 'Save Best' in the app to save one.")
