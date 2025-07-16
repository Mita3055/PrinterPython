VIDEO_DEVICES = {
    'video0': {
        'node': '/dev/video0',
        'capture_resolution': (8000, 6000),
        'preview_resolution': (640, 480),
        'focus_value': 120,  # Manual focus start value
        'rotate': True,
        'name': 'Camera_0'
    },
    'video2': {
        'node': '/dev/video2',
        'capture_resolution': (1920, 1080),
        'preview_resolution': (640, 480),
        'focus_value': None, 
        'rotate': False,
        'name': 'Camera_2'
    }
}

class Capacitor:
    def __init__(self, stem_len=None, arm_len=None, arm_count=None, gap=None, arm_gap=None, contact_patch_width=None):
        self.stem_len = stem_len
        self.arm_len = arm_len
        self.arm_count = arm_count
        self.gap = gap
        self.arm_gap = arm_gap
        self.contact_patch_width = contact_patch_width


class Printer:
    def __init__(self, extrusion, retraction, feed_rate, movement_speed, print_height, bed_height, z_hop, line_gap):
        self.extrusion = extrusion
        self.retraction = retraction
        self.feed_rate = feed_rate
        self.movement_speed = movement_speed
        self.print_height = print_height
        self.bed_height = bed_height
        self.z_hop = z_hop
        self.line_gap = line_gap

        self.pressure_passed_extrusion = False
        self.segment_length = 0
        self.target_pressure = 0
    
    def constPressure(self, target_pressure):
        """
        Enable pressure-based extrusion control
        
        Args:
            target_pressure: Target pressure in Newtons
        """
        self.pressure_passed_extrusion = True
        self.target_pressure = target_pressure
        print(f"Pressure-based extrusion enabled. Target pressure: {target_pressure} N")

    def set_print_height(self, print_height, bed_height= None):

        self.print_height = print_height
        # If bed_height is not provided, use the default value
        if bed_height is not None:
            self.bed_height = bed_height

# Capacitor Profiles
LargeCap = Capacitor(
    stem_len=20,
    arm_len=20,
    arm_count=4,
    gap=6,
    arm_gap=6,
    contact_patch_width=10,
)

# Standard Capacitor Profile
stdCap = Capacitor(
    stem_len=10,
    arm_len=10,
    arm_count=4,
    gap=3,
    arm_gap=4,
    contact_patch_width=3,
)

electroCellCap = Capacitor(
    stem_len=10,
    arm_len=8,
    arm_count=3,
    gap=2,
    arm_gap=2.5,
    contact_patch_width=3,
)

smallCap = Capacitor(
    stem_len=10,
    arm_len=5,
    arm_count=4,
    gap=1,
    arm_gap=2,
    contact_patch_width=5,
)

# Printer Profiles

# PVA Print Profile
pvaPrintProfile = Printer(
    extrusion=0.075,
    retraction=0.03,
    feed_rate=950,
    movement_speed=5000,
    print_height=1.9,
    bed_height=1.75,
    z_hop=5,
    line_gap=0.1,
)

# MXene Ink Print Profile
MXeneInkPrintProfile = Printer(
    extrusion=0.02,
    retraction=0.03,
    feed_rate=1300,
    movement_speed=5000,
    print_height=1.9,
    bed_height=1.75,
    z_hop=5,
    line_gap=0.3
)

# MXene Ink Print Profile
MXeneProfile2_20 = Printer(
    extrusion=0.008,
    retraction=0.04,
    feed_rate=1700,
    movement_speed=5000,
    print_height=0.5,
    bed_height=0.5,
    z_hop=5,
    line_gap=0.4
)

MXeneProfile2_20_slide = Printer(
    extrusion=0.01,
    retraction=0.04,
    feed_rate=1800,
    movement_speed=6000,
    print_height=1.05,
    bed_height=0.95,
    z_hop=5,
    line_gap=0.1
)

# MXene Ink Print Profile
MXeneProfile_pet_25G = Printer(
    extrusion=0.08,
    retraction=0.04,
    feed_rate=1200,
    movement_speed=5000,
    print_height=1.1,
    bed_height=1,
    z_hop=5,
    line_gap=0.6
)

MXeneProfile_pet_30G = Printer(
    extrusion=0.015,
    retraction=0.04,
    feed_rate=1650,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
)

MXeneProfile_1pNanoParticles_25G = Printer(
    extrusion=0.015,
    retraction=0.04,
    feed_rate=2000,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
    # 0.15mm above PET
)

MXeneProfile_2pNanoParticles_25G = Printer(
    extrusion=0.015,
    retraction=0.04,
    feed_rate=2500,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
    # 0.15mm above PET
)

MXeneProfile_3pNanoParticles_22G = Printer(
    extrusion=0.008,
    retraction=0.04,
    feed_rate=1100,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
    # 0.15mm above PET
)

MXeneProfile_5pNanoParticles_22G = Printer(
    extrusion=0.008,
    retraction=0.04,
    feed_rate=1350,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
    # 0.2mm above PET
)

MXeneProfile_10pNanoParticles_22G = Printer(
    extrusion=0.01,
    retraction=0.04,
    feed_rate=1500,
    movement_speed=6000,
    print_height=1.3,
    bed_height=1.3,
    z_hop=5,
    line_gap=0.1
    # 0.2mm above PET
) 