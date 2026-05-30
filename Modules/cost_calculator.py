def calculate_cost(total_placement_time_seconds: float, production_volume: int, hourly_rate: float, setup_cost: float, overhead_per_hour: float, efficiency: float, optimized_time_savings: float = 0) -> dict:
    """
    Translates physical SMT assembly actions into financial data.
    Model: Total Assembly Cost = Setup + (Labor Cost) + (Overhead Cost) + (Material Cost)
    
    Parameters:
    - total_placement_time_seconds: Total placement time per board in seconds
    - production_volume: Number of boards to produce
    - hourly_rate: Labor cost per hour (₹/hour)
    - setup_cost: Fixed setup cost for the batch (₹)
    - overhead_per_hour: Overhead cost per hour (₹/hour) - includes facility, utilities, depreciation
    - efficiency: Line efficiency factor (0.0 to 1.0)
    - optimized_time_savings: Time saved per board from feeder optimization (seconds)
    
    Formula:
    Time per board (hours) = ((Placement Time - Savings) / Efficiency) / 3600
    Total Time = Time per board × Volume
    Labor Cost = Total Time × Hourly Rate
    Overhead Cost = Total Time × Overhead Rate
    Total Cost = Setup + Labor + Overhead
    Cost Per Board = Total Cost / Volume
    """
    
    # Apply optimization savings if provided
    optimized_time = max(0, total_placement_time_seconds - optimized_time_savings)
    
    # 1. Adjust the ideal time by the real-world efficiency factor
    actual_time_seconds_per_board = optimized_time / efficiency
    time_per_board_hours = actual_time_seconds_per_board / 3600.0
    
    # 2. Calculate total time for the ENTIRE batch
    total_time_hours = time_per_board_hours * production_volume
    
    # 3. Calculate labor cost for the batch
    labor_cost = total_time_hours * hourly_rate
    
    # 4. Calculate overhead cost based on total production time
    overhead_cost = total_time_hours * overhead_per_hour
    
    # 5. Apply the mathematical model for Total Batch Cost
    total_assembly_cost = setup_cost + labor_cost + overhead_cost
    
    # 6. Calculate unit economics (Cost Per Board)
    if production_volume > 0:
        cost_per_board = total_assembly_cost / production_volume
    else:
        cost_per_board = 0.0
    
    # 7. Calculate theoretical cost without optimization
    theoretical_time_seconds = total_placement_time_seconds / efficiency
    theoretical_time_hours = (theoretical_time_seconds / 3600.0) * production_volume
    theoretical_cost = setup_cost + (theoretical_time_hours * hourly_rate) + (theoretical_time_hours * overhead_per_hour)
    
    # 8. Calculate savings from optimization
    optimization_savings = theoretical_cost - total_assembly_cost
    
    # 9. Calculate savings if efficiency improves
    theoretical_efficiency_cost = ((total_placement_time_seconds / 3600.0) * production_volume * (hourly_rate + overhead_per_hour)) + setup_cost
    efficiency_loss_cost = total_assembly_cost - theoretical_efficiency_cost
    
    # Return rounded financial values with additional metrics
    return {
        # Core cost metrics
        "labor_cost": round(labor_cost, 2),
        "overhead_cost": round(overhead_cost, 2),
        "setup_cost": round(setup_cost, 2),
        "total_cost": round(total_assembly_cost, 2),
        "cost_per_board": round(cost_per_board, 2),
        
        # Time metrics
        "total_production_hours": round(total_time_hours, 2),
        "time_per_board_hours": round(time_per_board_hours, 4),
        "time_per_board_seconds": round(actual_time_seconds_per_board, 2),
        "ideal_time_per_board_seconds": round(total_placement_time_seconds, 2),
        
        # Optimization metrics
        "optimization_time_savings": round(optimized_time_savings, 2),
        "optimization_cost_savings": round(optimization_savings, 2),
        "theoretical_cost_without_optimization": round(theoretical_cost, 2),
        
        # Efficiency impact
        "efficiency_used": round(efficiency * 100, 1),
        "efficiency_loss_cost": round(efficiency_loss_cost, 2),
        "theoretical_cost_at_100_percent": round(theoretical_efficiency_cost, 2),
        
        # Cost breakdown percentages
        "cost_breakdown": {
            "labor_percentage": round((labor_cost / total_assembly_cost) * 100, 1) if total_assembly_cost > 0 else 0,
            "overhead_percentage": round((overhead_cost / total_assembly_cost) * 100, 1) if total_assembly_cost > 0 else 0,
            "setup_percentage": round((setup_cost / total_assembly_cost) * 100, 1) if total_assembly_cost > 0 else 0
        },
        
        # Per unit breakdown
        "per_board": {
            "labor": round(labor_cost / production_volume, 2) if production_volume > 0 else 0,
            "overhead": round(overhead_cost / production_volume, 2) if production_volume > 0 else 0,
            "setup": round(setup_cost / production_volume, 2) if production_volume > 0 else 0
        }
    }