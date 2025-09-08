"""Console script for severstar_mfc_rs485."""

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from severstar_mfc_rs485 import SeverstarMFC, discover_mfc_devices
from severstar_mfc_rs485.protocol import ControlMode

app = typer.Typer()
console = Console()


@app.command()
def discover(port: str = typer.Argument(..., help="Serial port name")):
    """Discover MFC devices on the RS485 bus."""
    console.print(f"🔍 Discovering MFC devices on {port}...")
    
    try:
        devices = discover_mfc_devices(port)
        if devices:
            table = Table(title="Discovered MFC Devices", box=box.ROUNDED)
            table.add_column("Address", style="cyan")
            table.add_column("Hex", style="green")
            table.add_column("Description", style="white")
            
            for addr in devices:
                table.add_row(str(addr), f"0x{addr:02X}", f"Device {addr}")
            
            console.print(table)
        else:
            console.print("❌ No MFC devices found", style="red")
            
    except Exception as e:
        console.print(f"❌ Discovery failed: {e}", style="red")


@app.command()
def info(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get device information."""
    try:
        with SeverstarMFC(port, address) as mfc:
            info = mfc.get_device_info()
            
            table = Table(title=f"MFC Device Information (Address: {address})", box=box.ROUNDED)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in info.items():
                table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"❌ Failed to get device info: {e}", style="red")


@app.command()
def status(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get device status."""
    try:
        with SeverstarMFC(port, address) as mfc:
            status_info = mfc.get_status()
            
            table = Table(title=f"MFC Device Status (Address: {address})", box=box.ROUNDED)
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Unit", style="yellow")
            
            for key, value in status_info.items():
                if key == 'control_mode':
                    table.add_row("Control Mode", value, "")
                elif key == 'setpoint':
                    table.add_row("Setpoint", f"{value:.4f}", "FS")
                elif key == 'flow_rate':
                    table.add_row("Flow Rate", f"{value:.4f}", "FS")
                elif key == 'valve_output':
                    table.add_row("Valve Output", f"{value:.4f}", "")
                elif key == 'alarm_status':
                    table.add_row("Alarm Status", f"0x{value:02X}", "")
                elif key.endswith('_temperature'):
                    table.add_row(key.replace('_', ' ').title(), f"{value:.1f}", "°C")
            
            console.print(table)
            
    except Exception as e:
        console.print(f"❌ Failed to get device status: {e}", style="red")


@app.command()
def set_flow(
    port: str = typer.Argument(..., help="Serial port name"),
    flow_rate: float = typer.Argument(..., help="Flow rate as fraction of full scale (-1 to 1)"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Set flow rate setpoint."""
    try:
        with SeverstarMFC(port, address) as mfc:
            mfc.set_flow_rate(flow_rate)
            console.print(f"✅ Flow rate set to {flow_rate:.4f} FS", style="green")
            
    except Exception as e:
        console.print(f"❌ Failed to set flow rate: {e}", style="red")


@app.command()
def get_flow(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get current flow rate."""
    try:
        with SeverstarMFC(port, address) as mfc:
            flow_rate = mfc.get_flow_rate()
            console.print(f"📊 Current flow rate: {flow_rate:.4f} FS", style="green")
            
    except Exception as e:
        console.print(f"❌ Failed to get flow rate: {e}", style="red")


@app.command()
def set_mode(
    port: str = typer.Argument(..., help="Serial port name"),
    mode: ControlMode = typer.Argument(..., help="Control mode (closed_loop, open_loop, manual_valve)"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Set control mode."""
    try:
        with SeverstarMFC(port, address) as mfc:
            mfc.set_control_mode(mode)
            console.print(f"✅ Control mode set to {mode.name}", style="green")
            
    except Exception as e:
        console.print(f"❌ Failed to set control mode: {e}", style="red")


@app.command()
def get_mode(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get current control mode."""
    try:
        with SeverstarMFC(port, address) as mfc:
            mode = mfc.get_control_mode()
            console.print(f"🎛️  Current control mode: {mode.name}", style="green")
            
    except Exception as e:
        console.print(f"❌ Failed to get control mode: {e}", style="red")


@app.command()
def calibration(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get calibration information."""
    try:
        with SeverstarMFC(port, address) as mfc:
            cal_info = mfc.get_calibration_info()
            
            table = Table(title=f"MFC Calibration Information (Address: {address})", box=box.ROUNDED)
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Unit", style="yellow")
            
            for key, value in cal_info.items():
                if key == 'full_scale_flow':
                    table.add_row("Full Scale Flow", f"{value:.4f}", "SCCM")
                elif key == 'zero_flow':
                    table.add_row("Zero Flow", f"{value:.4f}", "SCCM")
                elif key == 'gas_type':
                    table.add_row("Gas Type", str(value), "")
                elif key == 'gas_conversion_factor':
                    table.add_row("Gas Conversion Factor", f"{value:.4f}", "")
                elif key == 'null_value':
                    table.add_row("Null Value", f"{value:.4f}", "FS")
            
            console.print(table)
            
    except Exception as e:
        console.print(f"❌ Failed to get calibration info: {e}", style="red")


@app.command()
def totalizer(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Get totalizer information."""
    try:
        with SeverstarMFC(port, address) as mfc:
            totalizer_info = mfc.get_totalizer_info()
            
            table = Table(title=f"MFC Totalizer Information (Address: {address})", box=box.ROUNDED)
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Unit", style="yellow")
            
            table.add_row("Total Flow", f"{totalizer_info['total_flow']:.4f}", "SCCM")
            # Convert seconds to hours:minutes:seconds
            seconds = totalizer_info['operating_time']
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            table.add_row("Operating Time", f"{hours:02d}:{minutes:02d}:{seconds:02d}", "HH:MM:SS")
            
            console.print(table)
            
    except Exception as e:
        console.print(f"❌ Failed to get totalizer info: {e}", style="red")


@app.command()
def reset_totalizer(
    port: str = typer.Argument(..., help="Serial port name"),
    address: int = typer.Option(32, "--address", "-a", help="Device address (32-95)")
):
    """Reset total accumulated flow."""
    try:
        with SeverstarMFC(port, address) as mfc:
            mfc.commands.reset_totalizer()
            console.print("✅ Totalizer reset successfully", style="green")
            
    except Exception as e:
        console.print(f"❌ Failed to reset totalizer: {e}", style="red")


if __name__ == "__main__":
    app()
