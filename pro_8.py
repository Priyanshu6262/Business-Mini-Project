import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =======================
# Load Dataset
# =======================
try:
    df = pd.read_csv("shopping_behavior_updated.csv")
except FileNotFoundError:
    root = tk.Tk()
    root.withdraw() 
    messagebox.showerror("Error", "Dataset not found! Please make sure 'shopping_behavior_updated.csv' is in the same folder.")
    root.destroy()
    raise SystemExit

# Basic cleaning and type conversion
df.dropna(inplace=True)
if 'Purchase Amount (USD)' in df.columns:
    df['Purchase Amount (USD)'] = df['Purchase Amount (USD)'].astype(float)
if 'Age' in df.columns:
    df['Age'] = df['Age'].astype(int)

# Create 'Age Group' column for summary stats
age_bins = [0, 25, 35, 45, 55, 65, 100]
age_labels = ["<25", "25–35", "35–45", "45–55", "55–65", "65+"]
df['Age Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels, right=True, include_lowest=True)

# =======================
# Main Window
# =======================
root = tk.Tk()
root.title("📊 Filtered Business Analytics Dashboard")
root.geometry("1050x780")
root.config(bg="#f5f6fa")

header = tk.Label(root, text="🛒 Shopping Behavior Analyzer", font=("Helvetica", 20, "bold"), bg="#273c75", fg="white", pady=10)
header.pack(fill="x")

# Global variables for data and popup management
last_filtered_df = pd.DataFrame() 
current_detail_option = "Location" # Changed default to Location
details_popup = None # Set to None, will be initialized on first button click

# =======================
# Filters Section
# =======================
filter_frame = tk.Frame(root, bg="#f5f6fa")
filter_frame.pack(pady=10)

# Gender Filter
tk.Label(filter_frame, text="Gender:", bg="#f5f6fa", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
gender_var = tk.StringVar(value="All")
gender_values = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
ttk.Combobox(filter_frame, textvariable=gender_var, values=gender_values, state="readonly", width=12).grid(row=0, column=1, padx=5, pady=5)

# Age Range Filter
tk.Label(filter_frame, text="Age Range:", bg="#f5f6fa", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
age_var = tk.StringVar(value="All")
age_ranges = ["All", "18-25", "26-35", "36-45", "46-60", "60+"]
ttk.Combobox(filter_frame, textvariable=age_var, values=age_ranges, state="readonly", width=12).grid(row=0, column=3, padx=5, pady=5)

# Category Filter
tk.Label(filter_frame, text="Category:", bg="#f5f6fa", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)
category_var = tk.StringVar(value="All")
ttk.Combobox(filter_frame, textvariable=category_var, values=["All"] + sorted(df['Category'].unique().tolist()), width=12).grid(row=0, column=5, padx=5, pady=5)

# Season Filter
tk.Label(filter_frame, text="Season:", bg="#f5f6fa", font=("Arial", 10, "bold")).grid(row=0, column=6, padx=5, pady=5)
season_var = tk.StringVar(value="All")
ttk.Combobox(filter_frame, textvariable=season_var, values=["All"] + sorted(df['Season'].unique().tolist()), width=12).grid(row=0, column=7, padx=5, pady=5)


# =======================
# Frames for Graph and Summary
# =======================
main_frame = tk.Frame(root, bg="#f5f6fa")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

graph_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=1)
graph_frame.pack(side="left", fill="both", expand=True, padx=10)

summary_frame = tk.Frame(main_frame, bg="#E8EAF6", relief="solid", bd=1, width=350)
summary_frame.pack(side="right", fill="both")


# ======================
# Detail Report Functions (Modified)
# ======================
def update_details_display(option):
    """Updates the content of the detailed report based on the selected option."""
    global current_detail_option, details_popup
    current_detail_option = option
    
    # Check if the popup exists (it should, after the first call to show_details_popup)
    if details_popup is None:
        return

    # --- Clear and Setup ---
    # Clear old content (buttons, header, text box)
    for widget in details_popup.winfo_children():
        widget.destroy() 
        
    details_header = tk.Label(details_popup, text="Detailed Data View", font=("Helvetica", 16, "bold"), bg="#44bd32", fg="white", pady=10)
    details_header.pack(fill="x")
    
    control_frame = tk.Frame(details_popup, bg="#F4F4F4")
    control_frame.pack(pady=10)

    # Recreate the option buttons (REPLACED Category Sales with Location Sales)
    tk.Button(control_frame, text="Location Sales", command=lambda: update_details_display("Location"), bg="#FF7043" if option != "Location" else "#CC5500", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    tk.Button(control_frame, text="Color Popularity", command=lambda: update_details_display("Color"), bg="#66BB6A" if option != "Color" else "#338833", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    tk.Button(control_frame, text="Loyalty Laggards", command=lambda: update_details_display("Least Purchases"), bg="#FFCA28" if option != "Least Purchases" else "#CC9900", fg="black", font=("Arial", 10, "bold")).pack(side="left", padx=5)

    display_frame = tk.Frame(details_popup, bg="white")
    display_frame.pack(fill="both", expand=True, padx=10, pady=10)

    text_box = tk.Text(display_frame, wrap="word", font=("Consolas", 10), bg="#ecf0f1")
    text_box.pack(fill="both", expand=True, padx=5, pady=5)
    
    # --- Data Processing ---
    text = ""
    filtered_df = last_filtered_df.copy()

    if filtered_df.empty:
        text = "No data available to display details. Please run analysis first."
        
    elif option == "Location":
        # NEW default: Location Sales Analysis
        if 'Purchase Amount (USD)' in filtered_df.columns and 'Location' in filtered_df.columns:
            loc_sales = filtered_df.groupby('Location')['Purchase Amount (USD)'].sum().sort_values(ascending=False)
            text = "📍 Location Sales Analysis (Descending Total Sales):\n\n"
            for loc, sales in loc_sales.items():
                text += f"Location: {loc:<15} | Sales: ${sales:,.2f}\n"
            text += f"\n🏆 Top Location by Sales: {loc_sales.index[0]}"
        else:
            text = "Required columns (Purchase Amount or Location) are missing."
        
    elif option == "Color" and 'Color' in filtered_df.columns:
        color_counts = filtered_df['Color'].value_counts()
        text = "🎨 Item Color Popularity (Descending Count):\n\n"
        for col, count in color_counts.items():
            text += f"Color: {col:<10} | Count: {count}\n"
        text += f"\n🏆 Most Popular Color: {color_counts.idxmax()}"
        
    elif option == "Least Purchases":
        # Show 15 customers with least purchases (Loyalty Laggards)
        least_customers = filtered_df.nsmallest(15, 'Previous Purchases')[['Customer ID', 'Location', 'Previous Purchases']]
        text = "📉 15 Customers with Least Previous Purchases (Loyalty Laggards):\n\n"
        for _, row in least_customers.iterrows():
            text += f"ID: {row['Customer ID']} | Loc: {row['Location']:<10} | Prev Purchases: {row['Previous Purchases']}\n"
            
    else:
        text = "No data available for this report."
        
    text_box.insert("1.0", text)
    text_box.config(state=tk.DISABLED)

def show_details_popup():
    """Initializes the popup if it doesn't exist, then shows and updates it."""
    global details_popup
    
    if last_filtered_df.empty:
        messagebox.showwarning("No Data", "Please apply filters and run the analysis before viewing detailed reports.")
        return
        
    # === FIX: Lazy Initialization of Toplevel ===
    # Only create the details_popup Toplevel object the first time this function is called.
    if details_popup is None:
        details_popup = tk.Toplevel(root)
        details_popup.title("Detailed Reports")
        details_popup.geometry("600x500")
        details_popup.config(bg="#F4F4F4")
        details_popup.withdraw() # Start hidden after creation

    # Show the window and force an update
    details_popup.deiconify() 
    update_details_display(current_detail_option)


# =======================
# Analysis Function (Handles All Filters)
# =======================
def apply_age_filter(df, age_range):
    """Applies the age range filter to the DataFrame."""
    if age_range == "18-25":
        return df[(df["Age"] >= 18) & (df["Age"] <= 25)]
    elif age_range == "26-35":
        return df[(df["Age"] >= 26) & (df["Age"] <= 35)]
    elif age_range == "36-45":
        return df[(df["Age"] >= 36) & (df["Age"] <= 45)]
    elif age_range == "46-60":
        return df[(df["Age"] >= 46) & (df["Age"] <= 60)]
    elif age_range == "60+":
        return df[df["Age"] > 60]
    return df

def analyze_data():
    global last_filtered_df
    
    filtered_df = df.copy()
    
    # Apply Filters
    if gender_var.get() != "All":
        filtered_df = filtered_df[filtered_df["Gender"] == gender_var.get()]
    if age_var.get() != "All":
        filtered_df = apply_age_filter(filtered_df, age_var.get())
    if category_var.get() != "All":
        filtered_df = filtered_df[filtered_df['Category'] == category_var.get()]
    if season_var.get() != "All":
        filtered_df = filtered_df[filtered_df['Season'] == season_var.get()]

    if filtered_df.empty:
        messagebox.showwarning("No Data", "No records found for selected filters.")
        for widget in graph_frame.winfo_children(): widget.destroy()
        for widget in summary_frame.winfo_children(): widget.destroy()
        last_filtered_df = pd.DataFrame() 
        return

    last_filtered_df = filtered_df.copy() # Store for detailed popup

    # --- SUMMARY CALCULATIONS ---
    total_sales = filtered_df['Purchase Amount (USD)'].sum()
    avg_rating = round(filtered_df["Review Rating"].mean(), 2) if "Review Rating" in filtered_df.columns else "N/A"
    
    if not filtered_df['Age Group'].empty and filtered_df['Age Group'].nunique() > 0:
        filtered_df['Current Age Group'] = pd.cut(filtered_df['Age'], bins=age_bins, labels=age_labels, right=True, include_lowest=True)
        top_age_group = filtered_df['Current Age Group'].mode()[0]
    else:
        top_age_group = "N/A"
        
    product_col = "Item Purchased"
    rec_text = ""
    if product_col in filtered_df.columns:
        grouped = filtered_df.groupby(product_col)
        top_items = grouped.size().sort_values(ascending=False).head(3)
        avg_ratings_items = grouped["Review Rating"].mean() if "Review Rating" in filtered_df.columns else None
        
        for i, (item, count) in enumerate(top_items.items(), 1):
            avg_r = round(avg_ratings_items.get(item, 0), 2) if avg_ratings_items is not None else "N/A"
            rec_text += f" {i}. {item} | Sales: {count} | Avg Rtg: {avg_r}\n"
    else:
        rec_text = "No 'Item Purchased' column found."
    # --------------------------------------------------------------------

    # -------------------------
    # Visualization (Category-wise Sales Bar Chart)
    # -------------------------
    for widget in graph_frame.winfo_children(): widget.destroy()

    if "Category" in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered_df.groupby('Category')['Purchase Amount (USD)'].sum().sort_values(ascending=False).plot(
            kind='bar', color='#4A90E2', ax=ax)
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Sales (USD)")
        ax.set_title("Category-wise Total Sales", fontsize=12)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    else:
        tk.Label(graph_frame, text="No category data available for plotting.", bg="white").pack(padx=20, pady=20)

    # -------------------------
    # Update Summary Frame
    # -------------------------
    for widget in summary_frame.winfo_children(): widget.destroy()
    
    tk.Label(summary_frame, text="📊 Business Insights Summary", bg="#E8EAF6", fg="#1A237E", font=("Arial", 14, "bold")).pack(pady=10)
    
    summary_text = (
        f"💰 **Total Sales:** ${total_sales:,.2f}\n"
        f"⭐ **Avg Review Rating:** {avg_rating}\n"
        f"👥 **Most Active Age Group:** {top_age_group}\n"
        f"📋 **Total Records:** {len(filtered_df)}\n"
    )
    
    tk.Label(summary_frame, text=summary_text, justify="left", bg="#E8EAF6", font=("Arial", 12)).pack(padx=10, pady=5, anchor="w")
    
    tk.Label(summary_frame, text="⭐ Recommended Items (Top 3)", bg="#E8EAF6", fg="#0D47A1", font=("Arial", 13, "bold")).pack(padx=10, pady=(10, 0), anchor="w")
    tk.Label(summary_frame, text=rec_text, bg="#E8EAF6", font=("Consolas", 11), justify="left").pack(padx=10, pady=5, anchor="w")
    
    # Details button frame
    details_frame = tk.Frame(summary_frame, bg="#E8EAF6")
    details_frame.pack(pady=10, fill="x")
    tk.Button(details_frame, text="Detailed Reports", command=show_details_popup, bg="#1976D2", fg="white", font=("Arial", 12, "bold")).pack(fill="x", padx=10)
    
    # FIX: Force refresh the popup if it is visible and exists
    if details_popup is not None:
        root.update_idletasks() 
        if details_popup.winfo_ismapped():
            update_details_display(current_detail_option)


# =======================
# Buttons
# =======================
btn_frame = tk.Frame(root, bg="#f5f6fa")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="🔍 Apply Filter & Analyze", command=analyze_data, bg="#0097e6", fg="white", font=("Arial", 12, "bold"), width=25).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="❌ Exit Dashboard", command=root.quit, bg="#e84118", fg="white", font=("Arial", 12, "bold"), width=20).grid(row=0, column=1, padx=10)

# Run initial analysis on load
root.after(100, analyze_data)

# =======================
# Run Main Loop
# =======================
root.mainloop()