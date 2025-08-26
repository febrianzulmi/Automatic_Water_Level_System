#!/usr/bin/env python3
"""
Water Pump Control Service
Script untuk menjalankan sistem kontrol pompa sebagai service/daemon
"""

import sys
import time
import signal
import logging
from water_level_pump_control import WaterLevelPumpController

class WaterPumpService:
    def __init__(self):
        self.controller = None
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle system signals"""
        print(f"\n🛑 Menerima signal {signum}, menghentikan service...")
        self.stop()
        
    def start(self):
        """Start the service"""
        try:
            print("🚰 Memulai Water Pump Control Service...")
            self.controller = WaterLevelPumpController()
            self.running = True
            
            print("✅ Service berhasil dimulai")
            print("📊 Monitoring level air dan kontrol pompa aktif")
            print("🛑 Tekan Ctrl+C untuk menghentikan")
            
            # Run continuous monitoring
            self.controller.run_continuous_monitoring()
            
        except Exception as e:
            print(f"❌ Error memulai service: {e}")
            logging.error(f"Service error: {e}")
            sys.exit(1)
            
    def stop(self):
        """Stop the service"""
        if self.running:
            print("🛑 Menghentikan service...")
            self.running = False
            
            if self.controller:
                self.controller.cleanup()
                
            print("✅ Service berhasil dihentikan")
            sys.exit(0)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            service = WaterPumpService()
            service.start()
        elif sys.argv[1] == 'stop':
            print("❌ Gunakan Ctrl+C untuk menghentikan service")
        elif sys.argv[1] == 'restart':
            print("🔄 Restart service...")
            service = WaterPumpService()
            service.start()
        elif sys.argv[1] == 'status':
            # Check if service is running
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'water_pump_service.py' in str(proc.info['cmdline']):
                    print(f"✅ Service berjalan (PID: {proc.info['pid']})")
                    return
            print("❌ Service tidak berjalan")
        else:
            print("🚰 Water Pump Control Service")
            print("\nPenggunaan:")
            print("  python water_pump_service.py start    # Mulai service")
            print("  python water_pump_service.py status   # Cek status")
            print("  python water_pump_service.py restart  # Restart service")
    else:
        # Default: start service
        service = WaterPumpService()
        service.start()

if __name__ == "__main__":
    main()
