from fpdf import FPDF
import datetime
import os

def generate_report(summary, cost_result, production_volume=500, efficiency=85, machine_capacity=50, overhead_per_hour=500, hourly_rate=2500, setup_cost=2000, bom_name="BOM"):
    """Generates a stunning, professional PDF Manufacturing Report with modern design."""
    
    # Initialize PDF with better margins
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    
    # Define color palette (Factory-Quant Modern Theme)
    COLORS = {
        'primary': (37, 99, 235),      # Factory Blue
        'secondary': (139, 92, 246),   # Purple accent
        'dark': (15, 23, 42),          # Dark slate
        'light': (248, 250, 252),      # Off white
        'gray': (100, 116, 139),       # Slate gray
        'success': (16, 185, 129),     # Emerald green
        'warning': (245, 158, 11),     # Amber
        'border': (226, 232, 240)      # Light border
    }
    
    # ---------------------------------------------------------
    # 1. HEADER WITH GRADIENT EFFECT
    # ---------------------------------------------------------
    pdf.set_fill_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_fill_color(COLORS['secondary'][0], COLORS['secondary'][1], COLORS['secondary'][2])
    pdf.rect(0, 45, 210, 3, 'F')
    
    pdf.set_font("Helvetica", 'B', 28)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(12)
    pdf.cell(0, 12, "FACTORY-QUANT", ln=True, align='C')
    
    pdf.set_font("Helvetica", '', 12)
    pdf.set_text_color(220, 230, 250)
    pdf.cell(0, 8, "Automated SMT Manufacturing Intelligence Report", ln=True, align='C')
    
    # BOM Name
    pdf.set_font("Helvetica", 'I', 10)
    pdf.set_text_color(220, 230, 250)
    pdf.cell(0, 6, f"BOM: {bom_name}", ln=True, align='C')
    
    # Date stamp
    pdf.set_y(38)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(200, 210, 230)
    current_time = datetime.datetime.now().strftime('%d %B %Y | %H:%M')
    pdf.cell(0, 6, f"Generated: {current_time}", ln=True, align='R')
    
    # Reset position
    pdf.set_y(55)
    
    # ---------------------------------------------------------
    # HELPER FUNCTIONS
    # ---------------------------------------------------------
    
    def draw_section_header(title):
        """Draws a modern section header"""
        pdf.set_font("Helvetica", 'B', 16)
        pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
        pdf.cell(0, 10, title, ln=True)
        
        pdf.set_draw_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)
    
    def format_time(seconds):
        """Convert seconds to appropriate time format (minutes or seconds)"""
        if seconds >= 60:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes ({seconds:,.0f} seconds)"
        else:
            return f"{seconds:.0f} seconds"
    
    def draw_stat_card(x, y, label, value, unit=""):
        """Draws a modern stat card at specified position"""
        current_x = pdf.get_x()
        current_y = pdf.get_y()
        
        pdf.set_xy(x, y)
        
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(COLORS['border'][0], COLORS['border'][1], COLORS['border'][2])
        pdf.rect(x, y, 60, 30, 'DF')
        
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
        pdf.set_xy(x + 3, y + 5)
        pdf.cell(54, 6, label, align='C')
        
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_text_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
        pdf.set_xy(x, y + 14)
        
        if isinstance(value, (int, float)):
            if value >= 1000:
                value_str = f"{value:,.0f}"
            else:
                value_str = f"{value:,.2f}" if isinstance(value, float) and value % 1 != 0 else f"{value:,}"
        else:
            value_str = str(value)
        
        pdf.cell(60, 8, f"{value_str} {unit}", align='C')
        pdf.set_xy(current_x, current_y)
    
    # ---------------------------------------------------------
    # 2. EXECUTIVE SUMMARY
    # ---------------------------------------------------------
    draw_section_header("EXECUTIVE SUMMARY")
    
    total_slots = sum(summary['feeder_counts'].values())
    total_placement_time = round(summary['total_placement_time'], 2)
    
    draw_stat_card(15, pdf.get_y(), "Total Components", summary['total_components'], "pcs")
    draw_stat_card(75, pdf.get_y(), "Ideal Placement Time", total_placement_time, "sec/board")
    draw_stat_card(135, pdf.get_y(), "Feeder Slots Required", total_slots, "slots")
    
    pdf.ln(35)
    
    # ---------------------------------------------------------
    # 3. PRODUCTION DETAILS (Using Minutes - CORRECTED)
    # ---------------------------------------------------------
    draw_section_header("PRODUCTION ANALYSIS")
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
    
    pdf.set_x(15)
    pdf.cell(90, 8, "Production Volume:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, f"{production_volume:,} boards", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Line Efficiency:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, f"{efficiency}%", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Labor Rate:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, f"Rs. {hourly_rate}/hour", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Overhead Rate:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, f"Rs. {overhead_per_hour}/hour", ln=True)
    
    # Calculate times using cost_result values for consistency
    ideal_seconds = total_placement_time
    actual_seconds = cost_result.get('time_per_board_seconds', ideal_seconds / (efficiency / 100))
    ideal_batch_seconds = ideal_seconds * production_volume
    actual_batch_seconds = actual_seconds * production_volume
    
    ideal_batch_minutes = ideal_batch_seconds / 60
    actual_batch_minutes = actual_batch_seconds / 60
    lost_seconds = actual_batch_seconds - ideal_batch_seconds
    lost_minutes = lost_seconds / 60
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Ideal Placement Time (100% eff):", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
    pdf.cell(0, 8, f"{ideal_seconds:.2f} seconds per board", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, f"Actual Placement Time ({efficiency}% eff):", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
    pdf.cell(0, 8, f"{actual_seconds:.2f} seconds per board", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Total Batch Time:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
    if actual_batch_minutes >= 60:
        pdf.cell(0, 8, f"{actual_batch_minutes/60:.2f} hours ({actual_batch_minutes:.1f} minutes)", ln=True)
    else:
        pdf.cell(0, 8, f"{actual_batch_minutes:.1f} minutes ({actual_batch_seconds:.0f} seconds)", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Time Lost Due to Efficiency:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(245, 158, 11)
    lost_percentage = (lost_seconds / actual_batch_seconds) * 100 if actual_batch_seconds > 0 else 0
    pdf.cell(0, 8, f"{lost_seconds:.1f} seconds ({lost_percentage:.1f}% of total time)", ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    pdf.set_x(15)
    pdf.cell(90, 8, "Machine Feeder Capacity:", ln=False)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
    pdf.cell(0, 8, f"{machine_capacity} slots", ln=True)
    
    pdf.ln(10)
    # ---------------------------------------------------------
    # 4. FEEDER CONFIGURATION TABLE
    # ---------------------------------------------------------
    draw_section_header("FEEDER CONFIGURATION")
    
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
    pdf.cell(0, 6, "Machine feeder slot allocation requirements:", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_fill_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(90, 12, "Feeder Width", border=1, align='C', fill=True)
    pdf.cell(70, 12, "Quantity Required", border=1, align='C', fill=True, ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    row_count = 0
    for size, count in sorted(summary['feeder_counts'].items()):
        if row_count % 2 == 0:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
        pdf.cell(90, 10, str(size), border=1, align='L', fill=True)
        pdf.cell(70, 10, str(count), border=1, align='C', fill=True, ln=True)
        row_count += 1
    
    pdf.ln(8)
    
    if machine_capacity > 0:
        utilization = (total_slots / machine_capacity) * 100
    else:
        utilization = 0
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
    pdf.cell(0, 8, f"Capacity Utilization: {utilization:.1f}% ({total_slots}/{machine_capacity} slots)", ln=True)
    
    bar_width = 160
    bar_height = 6
    pdf.set_fill_color(230, 240, 250)
    pdf.rect(15, pdf.get_y() + 2, bar_width, bar_height, 'F')
    
    if utilization <= 70:
        pdf.set_fill_color(16, 185, 129)
    elif utilization <= 90:
        pdf.set_fill_color(245, 158, 11)
    else:
        pdf.set_fill_color(239, 68, 68)
    
    fill_width = min((utilization / 100) * bar_width, bar_width)
    pdf.rect(15, pdf.get_y() + 2, fill_width, bar_height, 'F')
    
    if utilization > 100:
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 6, f"WARNING: Exceeds machine capacity by {utilization - 100:.1f}% - Consolidation required!", ln=True)
    elif utilization > 90:
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.set_text_color(245, 158, 11)
        pdf.cell(0, 6, f"CAUTION: Near capacity limit - {utilization:.1f}% utilization", ln=True)
    else:
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.set_text_color(16, 185, 129)
        pdf.cell(0, 6, f"STATUS: Capacity OK", ln=True)
    
    pdf.ln(8)
    
       # ---------------------------------------------------------
    # 5. COST ANALYSIS (CORRECTED)
    # ---------------------------------------------------------
    draw_section_header("COST ANALYSIS")
    
    # Get values from cost_result
    labor_cost = cost_result.get('labor_cost', 0)
    overhead_cost = cost_result.get('overhead_cost', 0)
    setup_cost_value = cost_result.get('setup_cost', setup_cost)
    total_cost = cost_result.get('total_cost', 0)
    cost_per_board = cost_result.get('cost_per_board', 0)
    
    # --- Cost Breakdown Table ---
    pdf.set_x(15)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
    pdf.cell(0, 8, "Cost Breakdown", ln=True)
    pdf.ln(4)
    
    # Create a cost breakdown table
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 10, "Cost Component", border=1, align='C', fill=True)
    pdf.cell(50, 10, "Amount (Rs.)", border=1, align='C', fill=True)
    pdf.cell(45, 10, "Percentage", border=1, align='C', fill=True, ln=True)
    
    pdf.set_font("Helvetica", '', 11)
    cost_items = [
        ("Labor Cost", labor_cost),
        ("Overhead Cost", overhead_cost),
        ("Setup Cost", setup_cost_value),
        ("Total Batch Cost", total_cost),
    ]
    
    for i, (item, amount) in enumerate(cost_items):
        if i % 2 == 0:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
        pdf.cell(80, 10, item, border=1, align='L', fill=True)
        pdf.cell(50, 10, f"Rs. {amount:,.2f}", border=1, align='R', fill=True)
        
        if item != "Total Batch Cost":
            percentage = (amount / total_cost) * 100 if total_cost > 0 else 0
            pdf.cell(45, 10, f"{percentage:.1f}%", border=1, align='C', fill=True, ln=True)
        else:
            pdf.cell(45, 10, "100%", border=1, align='C', fill=True, ln=True)
    
    pdf.ln(8)
    
    # --- Cost per Board Calculation Detail ---
    pdf.set_x(15)
    pdf.set_font("Helvetica", 'I', 10)
    pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
    pdf.cell(0, 6, f"Cost Per Board = Total Batch Cost ÷ Production Volume", ln=True)
    pdf.cell(0, 6, f"= Rs. {total_cost:,.2f} ÷ {production_volume} boards", ln=True)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(COLORS['success'][0], COLORS['success'][1], COLORS['success'][2])
    pdf.cell(0, 6, f"= Rs. {cost_per_board:,.2f} per board", ln=True)
    
    pdf.ln(12)
    
    # --- Centered Green Box for Final Cost ---
    box_width = 130
    box_x = (210 - box_width) / 2
    box_y = pdf.get_y()
    box_height = 42
    
    pdf.set_fill_color(COLORS['success'][0], COLORS['success'][1], COLORS['success'][2])
    pdf.set_draw_color(COLORS['success'][0], COLORS['success'][1], COLORS['success'][2])
    pdf.rect(box_x, box_y, box_width, box_height, 'DF')
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(box_x, box_y + 8)
    pdf.cell(box_width, 6, "FINAL COST PER BOARD", align='C')
    
    pdf.set_font("Helvetica", 'B', 24)
    pdf.set_xy(box_x, box_y + 18)
    pdf.cell(box_width, 12, f"Rs. {cost_per_board:,.2f}", align='C')
    
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_xy(box_x, box_y + 30)
    pdf.set_text_color(240, 253, 244)
    pdf.cell(box_width, 5, f"Based on {production_volume} boards | {efficiency}% efficiency", align='C')
    
    # Safely move cursor below the box
    pdf.set_y(box_y + box_height + 15) 
    # ---------------------------------------------------------
    # 6. COMPONENT BREAKDOWN (if available)
    # ---------------------------------------------------------
    if 'component_counts' in summary and summary['component_counts']:
        # Check if we have enough space, if not add new page
        if pdf.get_y() > 230:
            pdf.add_page()
        
        draw_section_header("COMPONENT BREAKDOWN")
        
        pdf.set_font("Helvetica", '', 10)
        pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
        pdf.cell(0, 6, "Components by type:", ln=True)
        pdf.ln(4)
        
        pdf.set_font("Helvetica", 'B', 11)
        pdf.set_fill_color(COLORS['primary'][0], COLORS['primary'][1], COLORS['primary'][2])
        pdf.set_text_color(255, 255, 255)
        pdf.cell(100, 10, "Component Type", border=1, align='C', fill=True)
        pdf.cell(60, 10, "Quantity", border=1, align='C', fill=True, ln=True)
        
        pdf.set_font("Helvetica", '', 11)
        row_count = 0
        for comp_type, count in sorted(summary['component_counts'].items()):
            if row_count % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
            pdf.cell(100, 10, str(comp_type), border=1, align='L', fill=True)
            pdf.cell(60, 10, f"{count:,}", border=1, align='C', fill=True, ln=True)
            row_count += 1
        
        pdf.ln(8)
    
    # ---------------------------------------------------------
    # 7. RECOMMENDATIONS (if capacity exceeded)
    # ---------------------------------------------------------
    if utilization > 100:
        # Check if we have enough space
        if pdf.get_y() > 230:
            pdf.add_page()
        
        draw_section_header("RECOMMENDATIONS")
        
        pdf.set_font("Helvetica", '', 11)
        pdf.set_text_color(COLORS['dark'][0], COLORS['dark'][1], COLORS['dark'][2])
        
        recommendations = [
            "1. Reduce setup time by optimizing feeder placement",
            "2. Consolidate multiple feeders of the same component type",
            "3. Consider using multi-lane feeders for high-volume components",
            "4. Increase machine capacity or reduce batch size",
            "5. Implement just-in-time feeder setup to reduce changeovers"
        ]
        
        for rec in recommendations:
            pdf.cell(0, 7, rec, ln=True)
            pdf.ln(2)
    
    # ---------------------------------------------------------
    # 8. FOOTER WITH BRANDING
    # ---------------------------------------------------------
    pdf.set_y(-25)
    
    pdf.set_draw_color(COLORS['border'][0], COLORS['border'][1], COLORS['border'][2])
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(COLORS['gray'][0], COLORS['gray'][1], COLORS['gray'][2])
    pdf.cell(0, 5, "Factory-Quant SMT Intelligence Platform", ln=True, align='C')
    pdf.cell(0, 5, "Confidential Manufacturing Report | Generated Automatically", ln=True, align='C')
    
    pdf.set_y(-18)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 5, f"Page {pdf.page_no()}", align='R')
    
    # Create reports directory if it doesn't exist
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # Save with timestamp in filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_bom_name = "".join(c for c in bom_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"reports/SMT_Report_{safe_bom_name}_{timestamp}.pdf"
    pdf.output(filename)
    
    return filename