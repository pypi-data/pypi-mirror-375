"""
Dizzy - Brick Schema Classes for Bob
"""

from rdflib import URIRef
from bob.core import bind_namespace, Node as _Node, Equipment as _Equipment
from bob.equipment.hvac.fan import Fan as _Fan
from bob.equipment.hvac.pump import Pump as _Pump
from bob.sensor.sensor import Sensor as _Sensor
from bob.sensor.temperature import AirTemperatureSensor as _AirTemperatureSensor

_namespace = BRICK = bind_namespace("brick", "https://brickschema.org/schema/Brick#")


class Entity(_Node):
    pass


class Class(Entity, _Node):
    pass


class Collection(Class, Entity):
    pass


class EV_Charging_Hub(Collection):
    pass


class Electric_Vehicle_Charging_Hub(Collection):
    """
    A collection of charging stations for charging electric vehicles. A
    hub may be located in a parking lot, for example
    """

    pass


class Loop(Collection):
    """
    A collection of connected equipment; part of a System
    """

    pass


class Air_Loop(Loop):
    """
    The set of connected equipment serving one path of air
    """

    pass


class Water_Loop(Loop):
    """
    A collection of equipment that transport and regulate water among each
    other
    """

    pass


class Chilled_Water_Loop(Water_Loop):
    """
    A collection of equipment that transport and regulate chilled water
    among each other
    """

    pass


class Condenser_Water_Loop(Water_Loop):
    """
    A collection of equipment that transport and regulate condenser water
    among each other
    """

    pass


class Domestic_Water_Loop(Water_Loop):
    pass


class Hot_Water_Loop(Water_Loop):
    """
    A collection of equipment that transport and regulate hot water among
    each other
    """

    pass


class PV_Array(Collection):
    pass


class Photovoltaic_Array(Collection):
    """
    A collection of photovoltaic panels
    """

    pass


class Portfolio(Collection):
    """
    A collection of sites
    """

    pass


class System(Collection):
    """
    A System is a combination of equipment and auxiliary devices (e.g.,
    controls, accessories, interconnecting means, and termi­nal elements)
    by which energy is transformed so it performs a specific function such
    as HVAC, service water heating, or lighting. (ASHRAE Dictionary).
    """

    pass


class Automatic_Tint_Window_Array(System):
    """
    An array of Automatic Tint Windows.
    """

    pass


class Domestic_Hot_Water_System(System):
    """
    The equipment, devices and conduits that handle the production and
    distribution of domestic hot water in a building
    """

    pass


class Electrical_System(System):
    """
    Devices that serve or are part of the electrical subsystem in the
    building
    """

    pass


class Energy_System(Electrical_System):
    """
    A collection of devices that generates, stores or transports
    electricity
    """

    pass


class Energy_Generation_System(Energy_System):
    """
    A collection of devices that generates electricity
    """

    pass


class PV_Generation_System(Energy_Generation_System):
    """
    A collection of photovoltaic devices that generates energy
    """

    pass


class Energy_Storage_System(Energy_System):
    """
    A collection of devices that stores electricity
    """

    pass


class Battery_Energy_Storage_System(Energy_Storage_System):
    """
    A collection of batteries that provides energy storage, along with
    their supporting equipment
    """

    pass


class Gas_System(System):
    pass


class HVAC_System(System):
    """
    See Heating_Ventilation_Air_Conditioning_System
    """

    pass


class Heating_Ventilation_Air_Conditioning_System(System):
    """
    The equipment, distribution systems and terminals that provide, either
    collectively or individually, the processes of heating, ventilating or
    air conditioning to a building or portion of a building
    """

    pass


class Air_System(Heating_Ventilation_Air_Conditioning_System):
    """
    The equipment, distribution systems and terminals that introduce or
    exhaust, either collectively or individually, the air into and from
    the building
    """

    pass


class Ventilation_Air_System(Air_System):
    """
    The equipment, devices, and conduits that handle the introduction and
    distribution of ventilation air in the building
    """

    pass


class Refrigeration_System(Heating_Ventilation_Air_Conditioning_System):
    """
    System designed to remove heat from a space or substance, typically
    using a refrigerant in a closed loop
    """

    pass


class Steam_System(Heating_Ventilation_Air_Conditioning_System):
    """
    The equipment, devices and conduits that handle the production and
    distribution of steam in a building
    """

    pass


class VRF_System(Heating_Ventilation_Air_Conditioning_System):
    pass


class Water_System(Heating_Ventilation_Air_Conditioning_System):
    """
    The equipment, devices and conduits that handle the production and
    distribution of water in a building
    """

    pass


class Chilled_Water_System(Water_System):
    """
    The equipment, devices and conduits that handle the production and
    distribution of chilled water in a building
    """

    pass


class Condenser_Water_System(Water_System):
    """
    A heat rejection system consisting of (typically) cooling towers,
    condenser water pumps, chillers and the piping connecting the
    components
    """

    pass


class Hot_Water_System(Water_System):
    """
    The equipment, devices and conduits that handle the production and
    distribution of hot water in a building
    """

    pass


class Heat_Recovery_Hot_Water_System(Hot_Water_System):
    pass


class Preheat_Hot_Water_System(Hot_Water_System):
    pass


class Radiation_Hot_Water_System(Hot_Water_System):
    pass


class Reheat_Hot_Water_System(Hot_Water_System):
    pass


class Lighting_System(System):
    """
    The equipment, devices and interfaces that serve or are a part of the
    lighting subsystem in a building
    """

    pass


class Safety_System(System):
    pass


class Emergency_Air_Flow_System(Safety_System):
    pass


class Emergency_Power_Off_System(Safety_System):
    """
    A system that can power down a single piece of equipment or a single
    system from a single point
    """

    pass


class Fire_Safety_System(Safety_System):
    """
    A system containing devices and equipment that monitor, detect and
    suppress fire hazards
    """

    pass


class Shading_System(System):
    """
    Devices that can control daylighting through various means
    """

    pass


class Blind_Group(Shading_System):
    """
    A group of Blinds commonly attached to a single controller.
    """

    pass


class Equipment(Class, Entity, _Equipment):
    """
    devices that serve all or part of the building and may include
    electric power, lighting, transportation, or service water heating,
    including, but not limited to, furnaces, boilers, air conditioners,
    heat pumps, chillers, water heaters, lamps, luminaires, ballasts,
    elevators, escalators, or other devices or installations.
    """

    pass


class Camera(Equipment):
    pass


class Electrical_Equipment(Equipment):
    pass


class Breaker_Panel(Electrical_Equipment):
    """
    Breaker Panel distributes power into various end-uses.
    """

    pass


class Bus_Riser(Electrical_Equipment):
    """
    Bus Risers are commonly fed from a switchgear and rise up through a
    series of floors to the main power distribution source for each floor.
    """

    pass


class Electric_Vehicle_Charging_Port(Electrical_Equipment):
    """
    An individual point of attachment for charing a single electric
    vehicle
    """

    pass


class Electric_Vehicle_Charging_Station(Electrical_Equipment):
    """
    An individual piece of equipment supplying electrical power for
    charging electric vehicles. Contains 1 or more electric vehicle
    charging ports
    """

    pass


class Energy_Storage(Electrical_Equipment):
    """
    Devices or equipment that store energy in its various forms
    """

    pass


class Battery(Energy_Storage):
    """
    A container that stores chemical energy that can be converted into
    electricity and used as a source of power
    """

    pass


class Inverter(Electrical_Equipment):
    """
    A device that changes direct current into alternating current
    """

    pass


class Photovoltaic_Inverter(Inverter):
    """
     Converts direct current electricity generated by solar panels into
    alternating current
    """

    pass


class Motor_Control_Center(Electrical_Equipment):
    """
    The Motor Control Center is a specialized type of switchgear which
    provides electrical power to major mechanical systems in the building
    such as HVAC components.
    """

    pass


class PlugStrip(Electrical_Equipment):
    """
    A device containing a block of electrical sockets allowing multiple
    electrical devices to be powered from a single electrical socket.
    """

    pass


class Switchgear(Electrical_Equipment):
    """
    A main disconnect or service disconnect feeds power to a switchgear,
    which then distributes power to the rest of the building through
    smaller amperage-rated disconnects.
    """

    pass


class Automatic_Switch(Switchgear):
    """
    An automatic switch operates automatically in the event of some
    current threshold or other designed event. Criteria for automatic
    operation is generally a physical property of the switch.
    """

    pass


class Circuit_Breaker(Switchgear):
    """
    A circuit breaker is a safety device to prevent damage to devices in a
    circuit, such as electric motors, and wiring when the current flowing
    through the electrical circuit supersedes its design limits. It does
    this by removing the current from a circuit when an unsafe condition
    arises. Unlike a switch, a circuit breaker automatically does this and
    shuts off the power immediately.
    """

    pass


class Main_Circuit_Breaker(Circuit_Breaker):
    """
    All breaker panels generally have a main circuit breaker before the
    bus / MCBs. In some older panels there may be a Main Disconnect Switch
    instead. It is also possible to have a main disconnect switch, and a
    main circuit breaker in a panel.
    """

    pass


class Disconnect_Switch(Switchgear):
    """
    A disconnect switch performs the task of manually cutting or
    reconnecting power from an electrical supply by creating or closing an
    air insulation gap between two conduction points. Also known as an
    'Isolation Switch'.
    """

    pass


class Building_Disconnect_Switch(Disconnect_Switch):
    pass


class Main_Disconnect_Switch(Disconnect_Switch):
    """
    Building power is most commonly provided by utility company through a
    master disconnect switch (sometimes called a service disconnect) in
    the main electrical room of a building. The Utility Company provided
    master disconnect switch often owns or restricts access to this
    switch. There can also be other cases where a disconnect is placed
    into an electrical system to allow service cut-off to a portion of the
    building.
    """

    pass


class Isolation_Switch(Switchgear):
    """
    See 'Disconnect_Switch'
    """

    pass


class Transfer_Switch(Switchgear):
    """
    An electrical switch that switches a load between two (or more)
    sources.
    """

    pass


class Automatic_Transfer_Switch(Transfer_Switch, Automatic_Switch):
    """
    An automatic transfer switch (ATS) is a device that automatically
    transfers a power supply from its primary source to a backup source
    when it senses a failure or outage in the primary source.
    """

    pass


class Static_Transfer_Switch(Transfer_Switch, Automatic_Switch):
    """
    Similar to ATS, but utilises no moving parts in the switch to achieve
    much faster response times.
    """

    pass


class Transformer(Electrical_Equipment):
    """
    A Transformer is usually fed by a high-voltage source and then steps
    down the voltage to a lower-voltage feed for low-voltage application
    (such as lights). Transformers also can step up voltage, but this
    generally does not apply to in building distribution.
    """

    pass


class Elevator(Equipment):
    """
    A device that provides vertical transportation between floors, levels
    or decks of a building, vessel or other structure
    """

    pass


class Fire_Safety_Equipment(Equipment):
    pass


class Fire_Alarm(Fire_Safety_Equipment):
    pass


class Fire_Alarm_Control_Panel(Fire_Safety_Equipment):
    """
    Fire alarm panel is the controlling component of a fire alarm system.
    """

    pass


class Fire_Control_Panel(Fire_Safety_Equipment):
    """
    A panel-mounted device that provides status and control of a fire
    safety system
    """

    pass


class Heat_Detector(Fire_Safety_Equipment):
    pass


class Manual_Fire_Alarm_Activation_Equipment(Fire_Safety_Equipment):
    """
    A device for manually activating fire alarm
    """

    pass


class Fire_Alarm_Manual_Call_Point(Manual_Fire_Alarm_Activation_Equipment):
    """
    Manual alarm call points are designed for the purpose of raising an
    alarm manually once verification of a fire or emergency condition
    exists. by operating the push button or break glass the alarm signal
    can be raised.
    """

    pass


class Fire_Alarm_Pull_Station(Manual_Fire_Alarm_Activation_Equipment):
    """
    An active fire protection device (usually wall-mounted) that when
    activated initiates an alarm on a fire alarm system. In its simplest
    form the user activates the alarm by pulling the handle down.
    """

    pass


class Smoke_Detector(Fire_Safety_Equipment):
    pass


class Furniture(Equipment):
    """
    Movable objects intended to support various human activities such as
    seating, eating and sleeping
    """

    pass


class Stage_Riser(Furniture):
    """
    A low platform in a space or on a stage
    """

    pass


class Gas_Distribution(Equipment):
    """
    Utilize a gas distribution source to represent how gas is distributed
    across multiple destinations
    """

    pass


class HVAC_Equipment(Equipment):
    """
    See Heating_Ventilation_Air_Conditioning_System
    """

    pass


class AHU(HVAC_Equipment):
    """
    Assembly consisting of sections containing a fan or fans and other
    necessary equipment to perform one or more of the following functions:
    circulating, filtration, heating, cooling, heat recovery, humidifying,
    dehumidifying, and mixing of air. Is usually connected to an air-
    distribution system.
    """

    pass


class Air_Handler_Unit(HVAC_Equipment):
    """
    Assembly consisting of sections containing a fan or fans and other
    necessary equipment to perform one or more of the following functions:
    circulating, filtration, heating, cooling, heat recovery, humidifying,
    dehumidifying, and mixing of air. Is usually connected to an air-
    distribution system.
    """

    pass


class Air_Handling_Unit(HVAC_Equipment):
    pass


class DDAHU(Air_Handling_Unit):
    """
    See Dual_Duct_Air_Handling_Unit
    """

    pass


class DOAS(Air_Handling_Unit):
    """
    See Dedicated_Outdoor_Air_System_Unit
    """

    pass


class Dedicated_Outdoor_Air_System_Unit(Air_Handling_Unit):
    """
    A device that conditions and delivers 100% outdoor air to its assigned
    spaces. It decouples air-conditioning of the outdoor air, usually used
    to provide minimum outdoor air ventilation, from conditioning of the
    internal loads.
    """

    pass


class Dual_Duct_Air_Handling_Unit(Air_Handling_Unit):
    """
    An air handling unit that contains hot and cold decks to supply
    heating and cooling to a building
    """

    pass


class MAU(Air_Handling_Unit):
    """
    See Makeup_Air_Unit
    """

    pass


class Makeup_Air_Unit(Air_Handling_Unit):
    """
    A device designed to condition ventilation air introduced into a space
    or to replace air exhausted from a process or general area exhaust.
    The device may be used to prevent negative pressure within buildings
    or to reduce airborne contaminants in a space.
    """

    pass


class PAU(Air_Handling_Unit):
    """
    A type of AHU, use to pre-treat the outdoor air before feed to AHU
    """

    pass


class PreCooling_Air_Unit(Air_Handling_Unit):
    """
    A type of AHU, use to pre-treat the outdoor air before feed to AHU
    """

    _class_iri: URIRef = BRICK["Pre-Cooling_Air_Unit"]
    pass


class RTU(Air_Handling_Unit):
    """
    see Rooftop_Unit
    """

    pass


class Rooftop_Unit(Air_Handling_Unit):
    """
    Packaged air conditioner mounted on a roof, the conditioned air being
    discharged directly into the rooms below or through a duct system.
    """

    pass


class Air_Plenum(HVAC_Equipment):
    """
    A component of the HVAC the receives air from the air handling unit or
    room to distribute or exhaust to or from the building
    """

    pass


class Discharge_Air_Plenum(Air_Plenum):
    pass


class Return_Air_Plenum(Air_Plenum):
    """
    A component of the HVAC the receives air from the room to recirculate
    or exhaust to or from the building
    """

    pass


class Supply_Air_Plenum(Air_Plenum):
    """
    A component of the HVAC the receives air from the air handling unit to
    distribute to the building
    """

    pass


class Underfloor_Air_Plenum(Supply_Air_Plenum):
    """
    An open space between a structural concrete slab and the underside of
    a raised access floor system that connects to an air handling unit to
    receive conditioned and/or ventilating air before delivery to the
    room(s)
    """

    pass


class Branch_Selector(HVAC_Equipment):
    """
    A device in VRF systems that regulates the flow of refrigerant to
    different indoor units or branches, ensuring optimal distribution of
    heating or cooling according to the specific requirements of each zone
    or area in the building.
    """

    pass


class CRAC(HVAC_Equipment):
    pass


class CRAH(HVAC_Equipment):
    """
    a computer room air handler (CRAH) uses fans, cooling coils and a
    water-chiller system to remove heat.
    """

    pass


class Chiller(HVAC_Equipment):
    """
    Refrigerating machine used to transfer heat between fluids. Chillers
    are either direct expansion with a compressor or absorption type.
    """

    pass


class Absorption_Chiller(Chiller):
    """
    A chiller that utilizes a thermal or/and chemical process to produce
    the refrigeration effect necessary to provide chilled water. There is
    no mechanical compression of the refrigerant taking place within the
    machine, as occurs within more traditional vapor compression type
    chillers.
    """

    pass


class Air_Cooled_Chiller(Chiller):
    """
    A chiller that uses air to cool the refrigerant, used in various
    commercial and industrial cooling applications
    """

    pass


class Centrifugal_Chiller(Chiller):
    """
    A chiller that uses the vapor compression cycle to chill water. It
    throws off the heat collected from the chilled water plus the heat
    from the compressor to a water loop
    """

    pass


class Water_Cooled_Chiller(Chiller):
    """
    A chiller system using water in the heat exchange process, employed in
    industrial or commercial facilities for cooling
    """

    pass


class Cold_Deck(HVAC_Equipment):
    """
    Part of a dual duct air handling unit that supplies cooling to a
    building
    """

    pass


class Compressor(HVAC_Equipment):
    """
    (1) device for mechanically increasing the pressure of a gas. (2)
    often described as being either open, hermetic, or semihermetic to
    describe how the compressor and motor drive is situated in relation to
    the gas or vapor being compressed. Types include centrifugal, axial
    flow, reciprocating, rotary screw, rotary vane, scroll, or diaphragm.
    1. device for mechanically increasing the pressure of a gas. 2.
    specific machine, with or without accessories, for compressing
    refrigerant vapor.
    """

    pass


class Computer_Room_Air_Conditioning(HVAC_Equipment):
    """
    A device that monitors and maintains the temperature, air distribution
    and humidity in a network room or data center.
    """

    pass


class Standby_CRAC(Computer_Room_Air_Conditioning):
    """
    A CRAC that is activated as part of a lead/lag operation or when an
    alarm occurs in a primary unit
    """

    pass


class Computer_Room_Air_Handler(HVAC_Equipment):
    """
    a computer room air handler (CRAH) uses fans, cooling coils and a
    water-chiller system to remove heat.
    """

    pass


class Condensing_Unit(HVAC_Equipment):
    """
    An outdoor HVAC unit that typically condenses refrigerant from gas to
    liquid, integral to the refrigeration cycle. It comprises a condenser
    coil, compressor, fan, and potentially a reversing valve in heat pump
    applications.
    """

    pass


class Cooling_Only_Condensing_Unit(Condensing_Unit):
    pass


class Cooling_Only_Air_Source_Condensing_Unit(Cooling_Only_Condensing_Unit):
    pass


class Cooling_Only_Ground_Source_Condensing_Unit(Cooling_Only_Condensing_Unit):
    pass


class Cooling_Only_Water_Source_Condensing_Unit(Cooling_Only_Condensing_Unit):
    pass


class Heat_Pump_Condensing_Unit(Condensing_Unit):
    """
    An outdoor HVAC unit that functions in both heating and cooling modes.
    It includes a reversing valve along with a condenser coil and
    compressor, enabling the switch between cooling and heating by
    reversing refrigerant flow.
    """

    pass


class Heat_Pump_Air_Source_Condensing_Unit(Heat_Pump_Condensing_Unit):
    pass


class Heat_Pump_Ground_Source_Condensing_Unit(Heat_Pump_Condensing_Unit):
    pass


class Heat_Pump_Water_Source_Condensing_Unit(Heat_Pump_Condensing_Unit):
    pass


class Heat_Recovery_Condensing_Unit(Condensing_Unit):
    """
    An advanced outdoor HVAC unit equipped for both heating and cooling,
    with the added capability of heat recovery. It efficiently recycles
    heat from the cooling process for heating purposes, featuring
    components like a condenser coil, compressor, and heat recovery
    systems.
    """

    pass


class Heat_Recovery_Air_Source_Condensing_Unit(Heat_Recovery_Condensing_Unit):
    pass


class Heat_Recovery_Water_Source_Condensing_Unit(Heat_Recovery_Condensing_Unit):
    pass


class Cooling_Tower(HVAC_Equipment):
    """
    A cooling tower is a heat rejection device that rejects waste heat to
    the atmosphere through the cooling of a water stream to a lower
    temperature. Cooling towers may either use the evaporation of water to
    remove process heat and cool the working fluid to near the wet-bulb
    air temperature or, in the case of closed circuit dry cooling towers,
    rely solely on air to cool the working fluid to near the dry-bulb air
    temperature.
    """

    pass


class Damper(HVAC_Equipment):
    """
    Element inserted into an air-distribution system or element of an air-
    distribution system permitting modification of the air resistance of
    the system and consequently changing the airflow rate or shutting off
    the airflow.
    """

    pass


class Bypass_Damper(Damper):
    """
    A bypass damper is a type of damper that is employed in forced-air
    bypass applications to reduce the buildup of static pressure, usually
    when certain zone dampers are closed.
    """

    pass


class Economizer_Damper(Damper):
    """
    A damper that is part of an economizer that is used to module the flow
    of air
    """

    pass


class Exhaust_Damper(Damper):
    """
    A damper that modulates the flow of exhaust air
    """

    pass


class Isolation_Damper(Damper):
    """
    A damper that isolates a section of ductwork or other air handling
    system.
    """

    pass


class Mixed_Damper(Damper):
    """
    A damper that modulates the flow of the mixed outside and return air
    streams
    """

    pass


class Outside_Damper(Damper):
    """
    A damper that modulates the flow of outside air
    """

    pass


class Relief_Damper(Damper):
    """
    A damper that is a component of a Relief Air System, ensuring building
    doesn't become over-pressurised
    """

    pass


class Return_Damper(Damper):
    """
    A damper that modulates the flow of return air
    """

    pass


class Zone_Damper(Damper):
    """
    Dampers open and close to regulate zone temperatures in an HVAC
    system.
    """

    pass


class Dry_Cooler(HVAC_Equipment):
    """
    A dry cooler is a fluid cooler that uses air, a relatively dry, non-
    liquid fluid to accomplish process cooling.
    (https://submer.com/submer-academy/library/dry-cooler/)
    """

    pass


class Economizer(HVAC_Equipment):
    """
    Device that, on proper variable sensing, initiates control signals or
    actions to conserve energy. A control system that reduces the
    mechanical heating and cooling requirement.
    """

    pass


class Fan(HVAC_Equipment, _Fan):
    """
    Any device with two or more blades or vanes attached to a rotating
    shaft used to produce an airflow for the purpose of comfort,
    ventilation, exhaust, heating, cooling, or any other gaseous
    transport.
    """

    pass


class Booster_Fan(Fan):
    """
    Fan activated to increase airflow beyond what is provided by the
    default configuration
    """

    pass


class Ceiling_Fan(Fan):
    """
    A fan installed on the ceiling of a room for the purpose of air
    circulation
    """

    pass


class Cooling_Tower_Fan(Fan):
    """
    A fan that pulls air through a cooling tower and across the louvers
    where the water falls to aid in heat exchange by the process of
    evaporation
    """

    pass


class Discharge_Fan(Fan):
    """
    Fan moving air discharged from HVAC vents
    """

    pass


class Exhaust_Fan(Fan):
    """
    Fan moving exhaust air -- air that must be removed from a space due to
    contaminants
    """

    pass


class Fume_Hood(Exhaust_Fan):
    """
    A fume hood is a type of local exhaust ventilation device designed to
    protect users from exposure to hazardous fumes, vapors, and dust. It
    is typically mounted over a workspace, table, or shelf to capture and
    conduct unwanted gases away from the enclosed area.
    """

    pass


class Fresh_Air_Fan(Fan):
    pass


class Outside_Fan(Fan):
    """
    Fan moving outside air; air that is supplied into the building from
    the outdoors
    """

    pass


class Pressurization_Fan(Fan):
    """
    A pressurization fan is a device used to increase and maintain higher
    air pressure in a specified space compared to its surroundings.
    """

    pass


class Relief_Fan(Fan):
    """
    A fan that is a component of a Relief Air System, ensuring building
    doesn't become over-pressurised
    """

    pass


class Return_Fan(Fan):
    """
    Fan moving return air -- air that is circulated from the building back
    into the HVAC system
    """

    pass


class Standby_Fan(Fan):
    """
    Fan that is activated as part of a lead/lag operation or when a
    primary fan raises an alarm
    """

    pass


class Supply_Fan(Fan):
    """
    Fan moving supply air -- air that is supplied from the HVAC system
    into the building
    """

    pass


class Transfer_Fan(Fan):
    """
    A fan that transfers air from a space to another space.
    """

    pass


class Filter(HVAC_Equipment):
    """
    Device to remove gases from a mixture of gases or to remove solid
    material from a fluid
    """

    pass


class Final_Filter(Filter):
    """
    The last, high-efficiency filter installed in a sequence to remove the
    finest particulates from the substance being filtered
    """

    pass


class Intake_Air_Filter(Filter):
    """
    Filters air intake
    """

    pass


class Mixed_Air_Filter(Filter):
    """
    A filter that is applied to the mixture of recirculated and outside
    air
    """

    pass


class Pre_Filter(Filter):
    """
    A filter installed in front of a more efficient filter to extend the
    life of the more expensive higher efficiency filter
    """

    pass


class Return_Air_Filter(Filter):
    """
    Filters return air
    """

    pass


class HX(HVAC_Equipment):
    """
    See Heat_Exchanger
    """

    pass


class Heat_Exchanger(HVAC_Equipment):
    """
    A heat exchanger is a piece of equipment built for efficient heat
    transfer from one medium to another. The media may be separated by a
    solid wall to prevent mixing or they may be in direct contact (BEDES)
    """

    pass


class Coil(Heat_Exchanger):
    """
    Cooling or heating element made of pipe or tube that may or may not be
    finned and formed into helical or serpentine shape (ASHRAE Dictionary)
    """

    pass


class Cooling_Coil(Coil):
    """
    A cooling element made of pipe or tube that removes heat from
    equipment, machines or airflows. Typically filled with either
    refrigerant or cold water.
    """

    pass


class Chilled_Water_Coil(Cooling_Coil):
    """
    A cooling element made of pipe or tube that removes heat from
    equipment, machines or airflows that is filled with chilled water.
    """

    pass


class Direct_Expansion_Cooling_Coil(Cooling_Coil):
    pass


class Heating_Coil(Coil):
    """
    A heating element typically made of pipe, tube or wire that emits
    heat. Typically filled with hot water, or, in the case of wire, uses
    electricity.
    """

    pass


class Direct_Expansion_Heating_Coil(Heating_Coil):
    pass


class Hot_Water_Coil(Heating_Coil):
    """
    A heating element typically made of pipe, tube or wire that emits heat
    that is filled with hot water.
    """

    pass


class Condenser_Heat_Exchanger(Heat_Exchanger):
    """
    A heat exchanger in which the primary heat transfer vapor changes its
    state to a liquid phase.
    """

    pass


class Evaporative_Heat_Exchanger(Heat_Exchanger):
    pass


class Heat_Wheel(Heat_Exchanger):
    """
    A rotary heat exchanger positioned within the supply and exhaust air
    streams of an air handling system in order to recover heat energy
    """

    pass


class Hot_Deck(HVAC_Equipment):
    """
    Part of a dual duct air handling unit that supplies heating to a
    building
    """

    pass


class Humidifier(HVAC_Equipment):
    """
    A device that adds moisture to air or other gases
    """

    pass


class Packaged_Heat_Pump(HVAC_Equipment):
    """
    A self-contained unit designed to transfer heat energy to or from a
    designated space, capable of offering both heating and cooling
    functions
    """

    pass


class Packaged_Air_Source_Heat_Pump(Packaged_Heat_Pump):
    """
    A self-contained unit that uses air as a heat source or sink for
    heating and cooling purposes.
    """

    pass


class Packaged_Water_Source_Heat_Pump(Packaged_Heat_Pump):
    """
    A self-contained unit that uses water as a heat source or sink for
    heating and cooling purposes.
    """

    pass


class Pump(HVAC_Equipment, _Pump):
    """
    Machine for imparting energy to a fluid, causing it to do work,
    drawing a fluid into itself through an entrance port, and forcing the
    fluid out through an exhaust port.
    """

    pass


class Booster_Pump(Pump):
    """
    Used to increase the pressure and flow of a fluid, typically water, in
    a system to ensure adequate supply where needed.
    """

    pass


class Circulator_Pump(Pump):
    """
    Used to move hot or cold water in a closed circuit, ensuring
    continuous fluid flow.
    """

    pass


class Water_Pump(Pump):
    """
    A pump that performs work on water
    """

    pass


class Chilled_Water_Pump(Water_Pump):
    """
    A pump that performs work on chilled water; typically part of a
    chilled water system
    """

    pass


class Chilled_Water_Booster_Pump(Chilled_Water_Pump, Booster_Pump):
    """
    Used to increase the pressure and flow of chilled water in a system to
    ensure adequate supply where needed.
    """

    pass


class Chilled_Water_Circulator_Pump(Chilled_Water_Pump, Circulator_Pump):
    """
    Used to move chilled water in a closed circuit, ensuring continuous
    flow.
    """

    pass


class Condenser_Water_Pump(Water_Pump):
    """
    A pump that is part of a condenser system; the pump circulates
    condenser water from the chiller back to the cooling tower
    """

    pass


class Condenser_Water_Booster_Pump(Condenser_Water_Pump, Booster_Pump):
    """
    Used to increase the pressure and flow of condenser water in a system
    to ensure adequate supply where needed.
    """

    pass


class Condenser_Water_Circulator_Pump(Condenser_Water_Pump, Circulator_Pump):
    """
    Used to move chilled water in a closed circuit, ensuring continuous
    flow.
    """

    pass


class Hot_Water_Pump(Water_Pump):
    """
    A pump that performs work on hot water; typically part of a hot water
    system
    """

    pass


class Hot_Water_Booster_Pump(Hot_Water_Pump, Booster_Pump):
    """
    Used to increase the pressure and flow of hot water in a system to
    ensure adequate supply where needed.
    """

    pass


class Hot_Water_Circulator_Pump(Hot_Water_Pump, Circulator_Pump):
    """
    Used to move hot water in a closed circuit, ensuring continuous flow.
    """

    pass


class Domestic_Hot_Water_Circulator_Pump(Hot_Water_Circulator_Pump):
    """
    Used to move domestic hot water in a closed circuit, ensuring
    continuous flow.
    """

    pass


class Refrigerant_Metering_Device(HVAC_Equipment):
    """
    Responsible for regulating refrigerant flow, which includes mechanisms
    like TXVs, EXVs, and capillary tubes
    """

    pass


class Capillary_Tube_Metering_Device(Refrigerant_Metering_Device):
    """
    A fixed orifice device in refrigeration systems that controls
    refrigerant flow based on its diameter and length, without moving
    parts
    """

    pass


class Electronic_Expansion_Valve(Refrigerant_Metering_Device):
    """
    A digitally controlled valve in HVAC systems that precisely regulates
    refrigerant flow.
    """

    pass


class Thermal_Expansion_Valve(Refrigerant_Metering_Device):
    """
    An type of metering device that automatically adjusts refrigerant flow
    based on temperature changes, using a sensing bulb
    """

    pass


class Space_Heater(HVAC_Equipment):
    """
    A heater used to warm the air in an enclosed area, such as a room or
    office
    """

    pass


class Terminal_Unit(HVAC_Equipment):
    """
    A device that regulates the volumetric flow rate and/or the
    temperature of the controlled medium.
    """

    pass


class Air_Diffuser(Terminal_Unit):
    """
    A device that is a component of the air distribution system that
    controls the delivery of conditioned and/or ventilating air into a
    room
    """

    pass


class Displacement_Flow_Air_Diffuser(Air_Diffuser):
    """
    An air diffuser that is designed for low discharge air speeds to
    minimize turbulence and induction of room air. This diffuser is used
    with displacement ventilation systems.
    """

    pass


class Jet_Nozzle_Air_Diffuser(Air_Diffuser):
    """
    An air diffuser that is designed to produce high velocity discharge
    air stream to throw the air over a large distance or target the air
    stream to a localize area
    """

    pass


class Laminar_Flow_Air_Diffuser(Air_Diffuser):
    """
    An air diffuser that is designed for low discharge air speeds to
    provide uniform and unidirectional air pattern which minimizes room
    air entrainment
    """

    pass


class CAV(Terminal_Unit):
    pass


class Chilled_Beam(Terminal_Unit):
    """
    A device with an integrated coil that performs sensible heating of a
    space via circulation of room air. Chilled Beams are not designed to
    perform latent cooling; see Induction Units. Despite their name,
    Chilled Beams may perform heating or cooling of a space depending on
    their configuration.
    """

    pass


class Active_Chilled_Beam(Chilled_Beam):
    """
    A Chilled Beam with an integral primary air connection that induces
    air flow through the device.
    """

    pass


class Passive_Chilled_Beam(Chilled_Beam):
    """
    A chilled beam that does not have an integral air supply and instead
    relies on natural convection to draw air through the device.
    """

    pass


class Constant_Air_Volume_Box(Terminal_Unit):
    """
    A terminal unit for which supply air flow rate is constant and the
    supply air temperature is varied to meet thermal load
    """

    pass


class FCU(Terminal_Unit):
    """
    See Fan_Coil_Unit
    """

    pass


class Fan_Coil_Unit(Terminal_Unit):
    """
    Terminal device consisting of a heating and/or cooling heat exchanger
    or 'coil' and fan that is used to control the temperature in the space
    where it is installed
    """

    pass


class Cassette_Fan_Coil_Unit(Fan_Coil_Unit):
    """
    A type of fan coil unit installed within the ceiling void, typically
    using a cassette for air delivery
    """

    pass


class Duct_Fan_Coil_Unit(Fan_Coil_Unit):
    """
    An inline HVAC component, the Duct Fan Coil Unit is integrated within
    the ductwork system, rather than within the served space, to
    distribute conditioned air through ducts to various areas or rooms.
    """

    pass


class Floor_Fan_Coil_Unit(Fan_Coil_Unit):
    """
    A fan coil unit installed on the floor, typically against a wall, for
    providing heating and cooling in residential or small office spaces
    """

    pass


class Horizontal_Fan_Coil_Unit(Fan_Coil_Unit):
    pass


class Wall_Fan_Coil_Unit(Fan_Coil_Unit):
    """
    A wall-mounted fan coil unit used for individual room heating and
    cooling, often found in hotels, apartments, and offices
    """

    pass


class Induction_Unit(Terminal_Unit):
    """
    A device with an primary air connection and integrated coil and
    condensate pan that performs sensible and latent cooling of a space.
    Essentially an Active Chilled Beam with a built in condensate pan.
    """

    pass


class Radiant_Panel(Terminal_Unit):
    """
    A temperature-controlled surface that provides fifty percent (50%) or
    more of the design heat transfer by thermal radiation.
    """

    pass


class ESS_Panel(Radiant_Panel):
    """
    See Embedded_Surface_System_Panel
    """

    pass


class Embedded_Surface_System_Panel(Radiant_Panel):
    """
    Radiant panel heating and cooling system where the energy heat source
    or sink is embedded in a radiant layer which is thermally insulated
    from the building structure.
    """

    pass


class RC_Panel(Radiant_Panel):
    """
    See Radiant_Ceiling_Panel
    """

    pass


class Radiant_Ceiling_Panel(Radiant_Panel):
    """
    Radiant panel heating and cooling system that are usually made from
    metal and suspended under the ceiling or insulated from the building
    structure.
    """

    pass


class TABS_Panel(Radiant_Panel):
    """
    See Thermally_Activated_Building_System_Panel
    """

    pass


class Thermally_Activated_Building_System_Panel(Radiant_Panel):
    """
    Radiant panel heating and cooling system where the energy heat source
    or sink is embedded in the building structure such as in slabs and
    walls.
    """

    pass


class Radiator(Terminal_Unit):
    """
    Heat exchangers designed to transfer thermal energy from one medium to
    another
    """

    pass


class Baseboard_Radiator(Radiator):
    """
    Steam, hydronic, or electric heating device located at or near the
    floor.
    """

    pass


class Electric_Radiator(Radiator):
    """
    Electric heating device
    """

    pass


class Electric_Baseboard_Radiator(Electric_Radiator, Baseboard_Radiator):
    """
    Electric heating device located at or near the floor
    """

    pass


class Hot_Water_Radiator(Radiator):
    """
    Radiator that uses hot water
    """

    pass


class Hot_Water_Baseboard_Radiator(Hot_Water_Radiator, Baseboard_Radiator):
    """
    Hydronic heating device located at or near the floor
    """

    pass


class Steam_Radiator(Radiator):
    """
    Radiator that uses steam
    """

    pass


class Steam_Baseboard_Radiator(Baseboard_Radiator, Steam_Radiator):
    """
    Steam heating device located at or near the floor
    """

    pass


class VAV(Terminal_Unit):
    """
    See Variable_Air_Volume_Box
    """

    pass


class Variable_Air_Volume_Box(Terminal_Unit):
    """
    A device that regulates the volume and temperature of air delivered to
    a zone by opening or closing a damper
    """

    pass


class RVAV(Variable_Air_Volume_Box):
    """
    See Variable_Air_Volume_Box_With_Reheat
    """

    pass


class Variable_Air_Volume_Box_With_Reheat(Variable_Air_Volume_Box):
    """
    A VAV box with a reheat coil mounted on the discharge end of the unit
    that can heat the air delivered to a zone
    """

    pass


class Wall_Air_Conditioner(HVAC_Equipment):
    """
    A wall air conditioner, also known as a window air conditioner when
    installed in a window frame, is a self-contained unit that cools a
    room by drawing in warm air, cooling it over a refrigerant coil, and
    recirculating it back into the space.
    """

    pass


class ICT_Equipment(Equipment):
    """
    Information and Communications Technology (ICT) equipment operates
    with a processor to process data or logic and create digital signals.
    """

    pass


class Audio_Visual_Equipment(ICT_Equipment):
    """
    Equipment related to sound and visual components such as speakers and
    displays.
    """

    pass


class Controller(ICT_Equipment):
    pass


class BACnet_Controller(Controller):
    pass


class Modbus_Controller(Controller):
    pass


class Data_Network_Equipment(ICT_Equipment):
    pass


class Ethernet_Port(Data_Network_Equipment):
    pass


class Ethernet_Switch(Data_Network_Equipment):
    pass


class Network_Router(Data_Network_Equipment):
    pass


class Network_Security_Equipment(Data_Network_Equipment):
    pass


class Wireless_Access_Point(Data_Network_Equipment):
    pass


class Gateway(ICT_Equipment):
    pass


class ICT_Hardware(ICT_Equipment):
    pass


class Server(ICT_Hardware):
    pass


class Tablet(ICT_Hardware):
    """
    A flat, handheld mobile computer, usually with a touchscreen
    """

    pass


class ICT_Rack(ICT_Equipment):
    pass


class Sensor_Equipment(ICT_Equipment):
    """
    A piece of equipment for sensing some physical properties
    """

    pass


class Daylight_Sensor_Equipment(Sensor_Equipment):
    pass


class IAQ_Sensor_Equipment(Sensor_Equipment):
    pass


class Leak_Detector_Equipment(Sensor_Equipment):
    pass


class Occupancy_Sensor_Equipment(Sensor_Equipment):
    pass


class People_Count_Sensor_Equipment(Sensor_Equipment):
    pass


class Thermostat(HVAC_Equipment, Sensor_Equipment):
    """
    An automatic control device used to maintain temperature at a fixed or
    adjustable setpoint.
    """

    pass


class Thermostat_Equipment(Sensor_Equipment):
    pass


class Vibration_Sensor_Equipment(Sensor_Equipment):
    pass


class Lighting_Equipment(Equipment):
    pass


class Interface(Lighting_Equipment):
    """
    A device that provides an occupant control over a lighting system
    """

    pass


class Switch(Interface):
    """
    A switch used to operate all or part of a lighting installation
    """

    pass


class Dimmer(Switch):
    """
    A switch providing continuous control over all or part of a lighting
    installation; typically potentiometer-based
    """

    pass


class Touchpanel(Interface):
    """
    A switch used to operate all or part of a lighting installation that
    uses a touch-based mechanism (typically resistive or capacitive)
    rather than a mechanical actuator
    """

    pass


class Lighting(Lighting_Equipment):
    pass


class Luminaire(Lighting):
    """
    A complete lighting unit consisting of a lamp or lamps and ballast(s)
    (when applicable) together with the parts designed to distribute the
    light, to position and protect the lamps, and to connect the lamps to
    the power supply.
    """

    pass


class Luminaire_Driver(Lighting):
    """
    A power source for a luminaire
    """

    pass


class Meter(Equipment):
    """
    A device that measure usage or consumption of some media --- typically
    a form energy or power.
    """

    pass


class Building_Meter(Meter):
    """
    A meter that measures usage or consumption of some media for a whole
    building
    """

    pass


class Electrical_Meter(Meter):
    """
    A meter that measures the usage or consumption of electricity
    """

    pass


class Building_Electrical_Meter(Electrical_Meter, Building_Meter):
    """
    A meter that measures the usage or consumption of electricity of a
    whole building
    """

    pass


class Gas_Meter(Meter):
    """
    A meter that measures the usage or consumption of gas
    """

    pass


class Building_Gas_Meter(Gas_Meter, Building_Meter):
    """
    A meter that measures the usage or consumption of gas of a whole
    building
    """

    pass


class Thermal_Power_Meter(Meter):
    """
    A standalone thermal power meter
    """

    pass


class Waste_Meter(Meter):
    """
    A Waste Meter is used for tracking and categorizing various waste
    types in a building, aiding in waste management facilitating waste
    reduction, recycling, and disposal strategies.
    """

    pass


class Water_Meter(Meter):
    """
    A meter that measures the usage or consumption of water
    """

    pass


class Building_Water_Meter(Water_Meter, Building_Meter):
    """
    A meter that measures the usage or consumption of water of a whole
    building
    """

    pass


class Chilled_Water_Meter(Water_Meter):
    """
    A meter that measures the usage or consumption of chilled water
    """

    pass


class Building_Chilled_Water_Meter(Chilled_Water_Meter, Building_Meter):
    """
    A meter that measures the usage or consumption of chilled water of a
    whole building
    """

    pass


class Hot_Water_Meter(Water_Meter):
    """
    A meter that measures the usage or consumption of hot water
    """

    pass


class Building_Hot_Water_Meter(Hot_Water_Meter, Building_Meter):
    """
    A meter that measures the usage or consumption of hot water of a whole
    building
    """

    pass


class Motor(Equipment):
    """
    A machine in which power is applied to do work by the conversion of
    various forms of energy into mechanical force and motion.
    """

    pass


class VFD(Motor):
    """
    Electronic device that varies its output frequency to vary the
    rotating speed of a motor, given a fixed input frequency. Used with
    fans or pumps to vary the flow in the system as a function of a
    maintained pressure.
    """

    pass


class Variable_Frequency_Drive(Motor):
    """
    Electronic device that varies its output frequency to vary the
    rotating speed of a motor, given a fixed input frequency. Used with
    fans or pumps to vary the flow in the system as a function of a
    maintained pressure.
    """

    pass


class Fan_VFD(Variable_Frequency_Drive):
    """
    Variable-frequency drive for fans
    """

    pass


class Heat_Wheel_VFD(Variable_Frequency_Drive):
    """
    A VFD that drives a heat wheel
    """

    pass


class Pump_VFD(Variable_Frequency_Drive):
    """
    Variable-frequency drive for pumps
    """

    pass


class PV_Panel(Equipment):
    """
    An integrated assembly of interconnected photovoltaic cells designed
    to deliver a selected level of working voltage and current at its
    output terminals packaged for protection against environment
    degradation and suited for incorporation in photovoltaic power
    systems.
    """

    pass


class Relay(Equipment):
    """
    an electrically operated switch
    """

    pass


class Safety_Equipment(Equipment):
    pass


class AED(Safety_Equipment):
    pass


class Automated_External_Defibrillator(Safety_Equipment):
    pass


class Emergency_Wash_Station(Safety_Equipment):
    pass


class Drench_Hose(Emergency_Wash_Station):
    pass


class Eye_Wash_Station(Emergency_Wash_Station):
    pass


class Safety_Shower(Emergency_Wash_Station):
    pass


class First_Aid_Kit(Safety_Equipment):
    pass


class Security_Equipment(Equipment):
    pass


class Access_Control_Equipment(Security_Equipment):
    pass


class Access_Reader(Access_Control_Equipment):
    pass


class Intercom_Equipment(Security_Equipment):
    pass


class Emergency_Phone(Intercom_Equipment):
    pass


class Video_Intercom(Intercom_Equipment):
    pass


class Intrusion_Detection_Equipment(Security_Equipment):
    pass


class Video_Surveillance_Equipment(Security_Equipment):
    pass


class NVR(Video_Surveillance_Equipment):
    pass


class Network_Video_Recorder(Video_Surveillance_Equipment):
    pass


class Surveillance_Camera(Video_Surveillance_Equipment, Camera):
    pass


class Shading_Equipment(Equipment):
    pass


class Automatic_Tint_Window(Shading_Equipment):
    """
    A window with tint control.
    """

    pass


class Blind(Shading_Equipment):
    """
    A window covering.
    """

    pass


class Solar_Thermal_Collector(Equipment):
    """
    A type of solar panels that converts solar radiation into thermal
    energy.
    """

    pass


class PVT_Panel(PV_Panel, Solar_Thermal_Collector):
    """
    A type of solar panels that convert solar radiation into usable
    thermal and electrical energy
    """

    pass


class Steam_Distribution(Equipment):
    """
    Utilize a steam distribution source to represent how steam is
    distributed across multiple destinations
    """

    pass


class Tank(Equipment):
    """
    A container designed to hold or store fluids for various applications
    within a system.
    """

    pass


class Separation_Tank(Tank):
    """
    A tank used in conjunction with a filter to facilitate the separation
    of filtrate material for disposal.
    """

    pass


class Grease_Interceptor(Separation_Tank):
    """
    A larger, more industrial version of a grease trap designed to handle
    higher volumes of wastewater and more efficiently separate grease and
    fats.
    """

    pass


class Storage_Tank(Tank):
    """
    A specialized type of tank intended primarily for the storage of
    fluids or gases for extended periods.
    """

    pass


class Thermal_Energy_Storage_Tank(Storage_Tank):
    """
    A Thermal Energy Storage (TES) tank is a specialized container for
    storing thermal energy, enabling more efficient heating and cooling by
    balancing supply and demand. It helps reduce operational costs and
    minimizes the need for larger equipment.
    """

    pass


class Chilled_Water_Thermal_Energy_Storage_Tank(Thermal_Energy_Storage_Tank):
    """
    A Thermal Energy Storage (TES) tank is a specialized container for
    storing thermal energy, enabling more efficient cooling by balancing
    supply and demand. It helps reduce operational costs and minimizes the
    need for larger equipment.
    """

    pass


class Hot_Water_Thermal_Energy_Storage_Tank(Thermal_Energy_Storage_Tank):
    """
    A Thermal Energy Storage (TES) tank is a specialized container for
    storing thermal energy, enabling more efficient heating by balancing
    supply and demand. It helps reduce operational costs and minimizes the
    need for larger equipment.
    """

    pass


class Water_Storage_Tank(Storage_Tank):
    """
    A specialized type of tank intended for the storage of water for
    extended periods.
    """

    pass


class Chilled_Water_Storage_Tank(Water_Storage_Tank):
    """
    A tank specifically designed to store chilled water in HVAC systems.
    """

    pass


class Cold_Water_Storage_Tank(Water_Storage_Tank):
    """
    A tank used to store cold water, usually in a building's water supply
    system.
    """

    pass


class Fire_Sprinkler_Water_Storage_Tank(Water_Storage_Tank):
    """
    A specialized tank intended to store water that can be quickly
    accessed for fire suppression.
    """

    pass


class Hot_Water_Storage_Tank(Water_Storage_Tank):
    """
    A tank designed to store hot water in an HVAC system.
    """

    pass


class Rain_Water_Storage_Tank(Water_Storage_Tank):
    """
    A tank engineered to capture and store rainwater, usually for non-
    potable uses.
    """

    pass


class Thermal_Expansion_Tank(Tank):
    """
    A tank designed to accommodate the expansion and contraction of a
    fluid, typically water, in a closed heating or cooling system.
    """

    pass


class Chilled_Water_Thermal_Expansion_Tank(Thermal_Expansion_Tank):
    """
    A thermal expansion tank designed specifically for chilled water
    systems.
    """

    pass


class Fire_Sprinkler_Thermal_Expansion_Tank(Thermal_Expansion_Tank):
    """
    A specialized thermal expansion tank that is part of a building's fire
    suppression system.
    """

    pass


class Hot_Water_Thermal_Expansion_Tank(Thermal_Expansion_Tank):
    """
    A thermal expansion tank used in hot water heating systems.
    """

    pass


class Valve(Equipment):
    """
    A device that regulates, directs or controls the flow of a fluid by
    opening, closing or partially obstructing various passageways
    """

    pass


class Bypass_Valve(Valve, HVAC_Equipment):
    """
    A type of valve installed in a bypass pipeline
    """

    pass


class Condenser_Water_Bypass_Valve(Bypass_Valve):
    """
    A valve installed in a bypass line of a condenser water loop
    """

    pass


class Differential_Pressure_Bypass_Valve(Bypass_Valve):
    """
    A 2-way, self contained proportional valve with an integral
    differential pressure adjustment setting.
    """

    pass


class Check_Valve(Valve):
    """
    Valve that allows fluid to flow in only one direction, preventing
    reverse flow.
    """

    pass


class Backflow_Preventer_Valve(Check_Valve):
    """
    Valve designed to prevent the reverse flow of fluid, typically water,
    thereby protecting potable water supplies from contamination or
    pollution.
    """

    pass


class Cooling_Valve(Valve, HVAC_Equipment):
    """
    A valve that controls air temperature by modulating the amount of cold
    water flowing through a cooling coil
    """

    pass


class Gas_Valve(Valve):
    pass


class HVAC_Valve(Valve, HVAC_Equipment):
    pass


class Heating_Valve(Valve, HVAC_Equipment):
    """
    A valve that controls air temperature by modulating the amount of hot
    water flowing through a heating coil
    """

    pass


class Reheat_Valve(Heating_Valve):
    """
    A valve that controls air temperature by modulating the amount of hot
    water flowing through a reheat coil
    """

    pass


class Return_Heating_Valve(Heating_Valve):
    """
    A valve installed on the return side of a heat exchanger
    """

    pass


class Isolation_Valve(Valve, HVAC_Equipment):
    """
    A valve that stops the flow of a fluid, usually for maintenance or
    safety purposes
    """

    pass


class Condenser_Water_Isolation_Valve(Isolation_Valve):
    """
    An isolation valve installed in the condenser water loop
    """

    pass


class Mixing_Valve(Valve):
    """
    Valve used for mixing hot and cold fluid to a desired temperature.
    """

    pass


class Electronic_Mixing_Valve(Mixing_Valve):
    """
    Electronically controlled valve for precise mixing of hot and cold
    fluid.
    """

    pass


class Thermostatic_Mixing_Valve(Mixing_Valve):
    """
    A valve that blends hot water with cold water to ensure constant, safe
    shower and bath outlet temperatures, preventing scalding.
    """

    pass


class Natural_Gas_Seismic_Shutoff_Valve(Valve):
    """
    Valves that automatically shut off your natural gas service when an
    earthquake of a sufficient magnitude occurs at the location.
    """

    pass


class Pressure_Reducing_Valve(Valve):
    """
    Valve used to reduce a high supply pressure to a usable level;
    maintains uniform outlet pressure despite inlet pressure variation.
    """

    pass


class Pressure_Regulator_Valve(Valve):
    """
    Device to maintain controlled downstream fluid pressure with varying
    upstream pressure.
    """

    pass


class Gas_Pressure_Regulator_Valve(Pressure_Regulator_Valve, Gas_Valve):
    """
    Valve designed to maintain controlled downstream gas pressure with
    varying upstream pressure.
    """

    pass


class Pressure_Relief_Valve(Valve):
    """
    Pressure-actuated valve to automatically relieve excessive pressure;
    prevents explosive shattering of the housing.
    """

    pass


class Refrigerant_Valve(Valve):
    """
    A valve controlling the flow or pressure of refrigerant in
    refrigeration or air conditioning systems, crucial for system
    efficiency
    """

    pass


class Reversing_Valve(Refrigerant_Valve):
    pass


class Steam_Valve(Valve, HVAC_Equipment):
    pass


class Steam_Pressure_Reducing_Valve(Steam_Valve, Pressure_Reducing_Valve):
    """
    Valve designed to reduce steam pressure from a high to a manageable
    level; maintains uniform steam outlet pressure.
    """

    pass


class Steam_Pressure_Relief_Valve(Steam_Valve, Pressure_Relief_Valve):
    """
    Valve designed to automatically relieve excessive steam pressure.
    """

    pass


class Water_Valve(Valve):
    """
    A valve that modulates the flow of water
    """

    pass


class Chilled_Water_Valve(Water_Valve, HVAC_Valve):
    """
    A valve that modulates the flow of chilled water
    """

    pass


class Condenser_Water_Valve(Water_Valve, HVAC_Valve):
    """
    A valve that modulates the flow of condenser water
    """

    pass


class Hot_Water_Valve(Water_Valve, Heating_Valve):
    """
    A valve regulating the flow of hot water
    """

    pass


class Domestic_Hot_Water_Valve(Hot_Water_Valve):
    """
    A valve regulating the flow of domestic hot water
    """

    pass


class Preheat_Hot_Water_Valve(Hot_Water_Valve):
    pass


class Makeup_Water_Valve(Water_Valve, HVAC_Valve):
    """
    A valve regulating the flow of makeup water into a water holding tank,
    e.g. a cooling tower, hot water tank
    """

    pass


class Water_Pressure_Reducing_Valve(Water_Valve, Pressure_Reducing_Valve):
    """
    Valve specifically designed to reduce high water pressure to a usable
    level; maintains uniform water outlet pressure.
    """

    pass


class Water_Pressure_Relief_Valve(Water_Valve, Pressure_Relief_Valve):
    """
    Valve designed to automatically relieve excessive water pressure.
    """

    pass


class Water_Distribution(Equipment):
    """
    Utilize a water distribution source to represent how water is
    distributed across multiple destinations (pipes)
    """

    pass


class Water_Heater(Equipment):
    """
    An apparatus for heating and usually storing hot water
    """

    pass


class Boiler(Water_Heater, HVAC_Equipment):
    """
    A closed, pressure vessel that uses fuel or electricity for heating
    water or other fluids to supply steam or hot water for heating,
    humidification, or other applications.
    """

    pass


class Electric_Boiler(Boiler):
    """
    A closed, pressure vessel that uses electricity for heating water or
    other fluids to supply steam or hot water for heating, humidification,
    or other applications.
    """

    pass


class Natural_Gas_Boiler(Boiler):
    """
    A closed, pressure vessel that uses natural gas for heating water or
    other fluids to supply steam or hot water for heating, humidification,
    or other applications.
    """

    pass


class Condensing_Natural_Gas_Boiler(Natural_Gas_Boiler):
    """
    A closed, pressure vessel that uses natural gas and heat exchanger
    that capture and reuse any latent heat for heating water or other
    fluids to supply steam or hot water for heating, humidification, or
    other applications.
    """

    pass


class Noncondensing_Natural_Gas_Boiler(Natural_Gas_Boiler):
    """
    A closed, pressure vessel that uses natural gas with no system to
    capture latent heat for heating water or other fluids to supply steam
    or hot water for heating, humidification, or other applications.
    """

    pass


class Collection_Basin_Water_Heater(Water_Heater):
    """
    Basin heaters prevent cold water basin freeze-up, e.g. in cooling
    towers, closed circuit fluid coolers, or evaporative condensers
    """

    pass


class Weather_Station(Equipment):
    """
    A dedicated weather measurement station
    """

    pass


class Location(Class, Entity):
    pass


class Building(Location):
    """
    An independent unit of the built environment with a characteristic
    spatial structure, intended to serve at least one function or user
    activity [ISO 12006-2:2013]
    """

    pass


class Parking_Structure(Building):
    """
    A building or part of a building devoted to vehicle parking
    """

    pass


class Floor(Location):
    """
    A level, typically representing a horizontal aggregation of spaces
    that are vertically bound. (referring to IFC)
    """

    pass


class Basement(Floor):
    """
    The floor of a building which is partly or entirely below ground
    level.
    """

    pass


class Parking_Level(Floor):
    """
    A floor of a parking structure
    """

    pass


class Rooftop(Floor):
    pass


class Outdoor_Area(Location):
    """
    A class of spaces that exist outside of a building
    """

    pass


class Bench_Space(Outdoor_Area):
    """
    For areas of play in a stadium, the area for partcipants and referees
    by the side of the field
    """

    pass


class Field_Of_Play(Outdoor_Area):
    """
    The area of a stadium where athletic events occur, e.g. the soccer
    pitch
    """

    pass


class Information_Area(Outdoor_Area):
    """
    An information booth or kiosk where visitors would look for
    information
    """

    pass


class Outside(Location):
    pass


class Region(Location):
    """
    A unit of geographic space, usually contigious or somehow related to a
    geopolitical feature
    """

    pass


class Site(Location):
    """
    A geographic region containing 0 or more buildings. Typically used as
    the encapsulating location for a collection of Brick entities through
    the hasPart/isPartOf relationships
    """

    pass


class Space(Location):
    """
    A part of the physical world or a virtual world whose 3D spatial
    extent is bounded actually or theoretically, and provides for certain
    functions within the zone it is contained in.
    """

    pass


class Common_Space(Space):
    """
    A class of spaces that are used by multiple people at the same time
    """

    pass


class Atrium(Common_Space):
    """
    a large open-air or skylight covered space surrounded by a building.
    """

    pass


class Auditorium(Common_Space):
    """
    A space for performances or larger gatherings
    """

    pass


class Cafeteria(Common_Space):
    """
    A space to serve food and beverages
    """

    pass


class Hallway(Common_Space):
    """
    A common space, used to connect other parts of a building
    """

    pass


class Lobby(Common_Space):
    """
    A space just after the entrance to a building or other space of a
    building, where visitors can wait
    """

    pass


class Employee_Entrance_Lobby(Lobby):
    """
    An open space near an entrance that is typicaly only used for
    employees
    """

    pass


class Visitor_Lobby(Lobby):
    """
    A lobby for visitors to the building. Sometimes used to distinguish
    from an employee entrance looby
    """

    pass


class Lounge(Common_Space):
    """
    A room for lesiure activities or relaxing
    """

    pass


class Majlis(Lounge):
    """
    In Arab countries, an Majlis is a private lounge where visitors are
    recieved and entertained
    """

    pass


class Entrance(Space):
    """
    The location and space of a building where people enter and exit the
    building
    """

    pass


class Gatehouse(Space):
    """
    The standalone building used to manage the entrance to a campus or
    building grounds
    """

    pass


class Media_Hot_Desk(Space):
    """
    A non-enclosed space used by members of the media temporarily to cover
    an event while they are present at a venue
    """

    pass


class Parking_Space(Space):
    """
    An area large enough to park an individual vehicle
    """

    pass


class Room(Space):
    """
    Base class for all more specific room types.
    """

    pass


class Ablutions_Room(Room):
    """
    A room for performing cleansing rituals before prayer
    """

    pass


class Break_Room(Room):
    """
    A space for people to relax while not working
    """

    pass


class Breakroom(Room):
    """
    A space for people to relax while not working
    """

    pass


class Conference_Room(Room):
    """
    A space dedicated in which to hold a meetings
    """

    pass


class Control_Room(Room):
    """
    A space from which operations are managed
    """

    pass


class Copy_Room(Room):
    """
    A room set aside for common office equipment, including printers and
    copiers
    """

    pass


class Exercise_Room(Room):
    """
    An indoor room used for exercise and physical activities
    """

    pass


class Food_Service_Room(Room):
    """
    A space used in the production, storage, serving, or cleanup of food
    and beverages
    """

    pass


class Concession(Food_Service_Room):
    """
    A space to sell food and beverages. Usually embedded in a larger space
    and does not include a space where people consume their purchases
    """

    pass


class Hospitality_Box(Room):
    """
    A room at a stadium, usually overlooking the field of play, that is
    physical separate from the other seating at the venue
    """

    pass


class Janitor_Room(Room):
    """
    A room set aside for the storage of cleaning equipment and supplies
    """

    pass


class Laboratory(Room):
    """
    facility acceptable to the local, national, or international
    recognized authority having jurisdiction and which provides uniform
    testing and examination procedures and standards for meeting design,
    manufacturing, and factory testing requirements.
    """

    pass


class Cold_Box(Laboratory):
    """
    in a gas separation unit, the insulated section that contains the low-
    temperature heat exchangers and distillation columns.
    """

    pass


class Environment_Box(Laboratory):
    """
    (also known as climatic chamber), enclosed space designed to create a
    particular environment.
    """

    pass


class Freezer(Laboratory):
    """
    cold chamber usually kept at a temperature of 22°F to 31°F (–5°C to
    –1°C), with high-volume air circulation.
    """

    pass


class Hot_Box(Laboratory):
    """
    hot air chamber forming part of an air handler.
    """

    pass


class Library(Room):
    """
    A place for the storage and/or consumption of physical media, e.g.
    books, periodicals, and DVDs/CDs
    """

    pass


class Loading_Dock(Room):
    """
    A part of a facility where delivery trucks can load and unload.
    Usually partially enclosed with specific traffic lanes leading to the
    dock
    """

    pass


class Mail_Room(Room):
    """
    A room where mail is recieved and sorted for distribution to the rest
    of the building
    """

    pass


class Massage_Room(Room):
    """
    Usually adjunct to an athletic facility, a private/semi-private space
    where massages are performed
    """

    pass


class Media_Room(Room):
    """
    A class of spaces related to the creation of media
    """

    pass


class Broadcast_Room(Media_Room):
    """
    A space to organize and manage a broadcast. Separate from studio
    """

    pass


class Media_Production_Room(Media_Room):
    """
    A enclosed space used by media professionals for the production of
    media
    """

    pass


class Studio(Media_Room):
    """
    A room used for the production or media, usually with either a
    specialized set or a specialized sound booth for recording
    """

    pass


class Medical_Room(Room):
    """
    A class of rooms used for medical purposes
    """

    pass


class First_Aid_Room(Medical_Room):
    """
    A room for a person with minor injuries can be treated or temporarily
    treated until transferred to a more advanced medical facility
    """

    pass


class Office(Room):
    """
    A class of rooms dedicated for work or study
    """

    pass


class Cubicle(Office):
    """
    A smaller space set aside for an individual, but not with a door and
    without full-height walls
    """

    pass


class Enclosed_Office(Office):
    """
    A space for individuals to work with walls and a door
    """

    pass


class Private_Office(Enclosed_Office):
    """
    An office devoted to a single individual, with walls and door
    """

    pass


class Shared_Office(Enclosed_Office):
    """
    An office used by multiple people
    """

    pass


class Team_Room(Enclosed_Office):
    """
    An office used by multiple team members for specific work tasks.
    Distinct from Conference Room
    """

    pass


class Open_Office(Office):
    """
    An open space used for work or study by mulitple people. Usuaully
    subdivided into cubicles or desks
    """

    pass


class Office_Kitchen(Room):
    """
    A common space, usually near or in a breakroom, where minor food
    preperation occurs
    """

    pass


class Prayer_Room(Room):
    """
    A room set aside for prayer
    """

    pass


class Reception(Room):
    """
    A space, usually in a lobby, where visitors to a building or space can
    go to after arriving at a building and inform building staff that they
    have arrived
    """

    pass


class Rest_Room(Room):
    """
    A room that provides toilets and washbowls. Alternate spelling of
    Restroom
    """

    pass


class Restroom(Room):
    """
    A room that provides toilets and washbowls.
    """

    pass


class Retail_Room(Room):
    """
    A space set aside for retail in a larger establishment, e.g. a gift
    shop in a hospital
    """

    pass


class Security_Service_Room(Room):
    """
    A class of spaces used by the security staff of a facility
    """

    pass


class Detention_Room(Security_Service_Room):
    """
    A space for the temporary involuntary confinement of people
    """

    pass


class Server_Room(Room):
    pass


class Service_Room(Room):
    """
    A class of spaces related to the operations of building subsystems,
    e.g. HVAC, electrical, IT, plumbing, etc
    """

    pass


class Electrical_Room(Service_Room):
    """
    A class of service rooms that house electrical equipment for a
    building
    """

    pass


class Battery_Room(Electrical_Room):
    """
    A room used to hold batteries for backup power
    """

    pass


class Generator_Room(Electrical_Room):
    """
    A room for electrical equipment, specifically electrical generators.
    """

    pass


class Transformer_Room(Electrical_Room):
    """
    An electrical room where electricity enters and is transformed to
    different voltages and currents by the equipment contained in the room
    """

    pass


class Mechanical_Room(Service_Room):
    """
    A class of service rooms where mechanical equipment (HVAC) operates
    """

    pass


class Pump_Room(Mechanical_Room):
    """
    A mechanical room that houses pumps
    """

    pass


class Plumbing_Room(Service_Room):
    """
    A service room devoted to the operation and routing of water in a
    building. Usually distinct from the HVAC subsystems.
    """

    pass


class Shower(Room):
    """
    A space containing showers, usually adjacent to an athletic or execise
    area
    """

    pass


class Sports_Service_Room(Room):
    """
    A class of spaces used in the support of sports
    """

    pass


class Storage_Room(Room):
    """
    A class of spaces used for storage
    """

    pass


class Hazardous_Materials_Storage(Storage_Room):
    """
    A storage space set aside (usually with restricted access) for the
    storage of materials that can be hazardous to living beings or the
    environment
    """

    pass


class Waste_Storage(Storage_Room):
    """
    A room used for storing waste such as trash or recycling
    """

    pass


class Telecom_Room(Room):
    """
    A class of spaces used to support telecommuncations and IT equipment
    """

    pass


class Distribution_Frame(Telecom_Room):
    """
    A class of spaces where the cables carrying signals meet and connect,
    e.g. a wiring closet or a broadcast downlink room
    """

    pass


class IDF(Distribution_Frame):
    """
    An room for an intermediate distribution frame, where cables carrying
    signals from the main distrubtion frame terminate and then feed out to
    endpoints
    """

    pass


class MDF(Distribution_Frame):
    """
    A room for the Main Distribution Frame, the central place of a
    building where cables carrying signals meet and connect to the outside
    world
    """

    pass


class Equipment_Room(Telecom_Room):
    """
    A telecommunications room where equipment that serves the building is
    stored
    """

    pass


class Switch_Room(Telecom_Room):
    """
    A telecommuncations room housing network switches
    """

    pass


class TETRA_Room(Telecom_Room):
    """
    A room used for local two-way radio networks, e.g. the portable radios
    carried by facilities staff
    """

    pass


class Wardrobe(Room):
    """
    Storage for clothing, costumes, or uniforms
    """

    pass


class Workshop(Room):
    """
    A space used to house equipment that can be used to repair or
    fabricate things
    """

    pass


class Ticketing_Booth(Space):
    """
    A room or space used to sell or distribute tickets to events at a
    venue
    """

    pass


class Tunnel(Space):
    """
    An enclosed space that connects buildings. Often underground
    """

    pass


class Vertical_Space(Space):
    """
    A class of spaces used to connect multiple floors or levels..
    """

    pass


class Elevator_Shaft(Vertical_Space):
    """
    The vertical space in which an elevator ascends and descends
    """

    pass


class Elevator_Space(Vertical_Space):
    """
    The vertical space in whcih an elevator ascends and descends
    """

    pass


class Riser(Vertical_Space):
    """
    A vertical shaft indented for installing building infrastructure e.g.,
    electrical wire, network communication wire, plumbing, etc
    """

    pass


class Staircase(Vertical_Space):
    """
    A vertical space containing stairs
    """

    pass


class Water_Tank(Space):
    """
    A space used to hold water. This will likely be deprecated in future
    releases of Brick for the sake of clarity w.r.t. equipment
    classification of tanks
    """

    pass


class Storey(Location):
    pass


class Wing(Location):
    """
    A wing is part of a building – or any feature of a building – that is
    subordinate to the main, central structure.
    """

    pass


class Zone(Location):
    """
    (1) a separately controlled heated or cooled space. (2) one occupied
    space or several occupied spaces with similar occupancy category,
    occupant density, zone air distribution effectiveness, and zone
    primary airflow per unit area. (3) space or group of spaces within a
    building for which the heating, cooling, or lighting requirements are
    sufficiently similar that desired conditions can be maintained
    throughout by a single controlling device.
    """

    pass


class Energy_Zone(Zone):
    """
    A space or group of spaces that are managed or monitored as one unit
    for energy purposes
    """

    pass


class Fire_Zone(Zone):
    """
    A logical subdivision of a building that is monitored for fire; may
    also have a classification for the type of fire hazard that can occur
    """

    pass


class HVAC_Zone(Zone):
    """
    a space or group of spaces, within a building with heating, cooling,
    and ventilating requirements, that are sufficiently similar so that
    desired conditions (e.g., temperature) can be maintained throughout
    using a single sensor (e.g., thermostat or temperature sensor).
    """

    pass


class Lighting_Zone(Zone):
    pass


class Measurable(Class, Entity):
    pass


class Quantity(Measurable):
    pass


class Substance(Measurable):
    pass


class Point(Class, Entity):
    pass


class Alarm(Point):
    """
    Alarm points are signals (either audible or visual) that alert an
    operator to an off-normal condition which requires some form of
    corrective action
    """

    pass


class Air_Alarm(Alarm):
    pass


class Air_Flow_Alarm(Air_Alarm):
    """
    An alarm related to air flow.
    """

    pass


class Air_Flow_Loss_Alarm(Air_Flow_Alarm):
    """
    An alarm that indicates loss in air flow.
    """

    pass


class High_Air_Flow_Alarm(Air_Flow_Alarm):
    """
    An alarm that indicates that the air flow is higher than normal.
    """

    pass


class Low_Air_Flow_Alarm(Air_Flow_Alarm):
    """
    An alarm that indicates that the air flow is lower than normal.
    """

    pass


class Low_Discharge_Air_Flow_Alarm(Low_Air_Flow_Alarm):
    """
    An alarm that indicates that the discharge air flow is lower than
    normal.
    """

    pass


class Low_Supply_Air_Flow_Alarm(Low_Air_Flow_Alarm):
    pass


class CO2_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    presence of carbon dioxide.
    """

    pass


class High_CO2_Alarm(CO2_Alarm):
    """
    A device that indicates high concentration of carbon dioxide.
    """

    pass


class Change_Filter_Alarm(Alarm):
    """
    An alarm that indicates that a filter must be changed
    """

    pass


class Communication_Loss_Alarm(Alarm):
    """
    An alarm that indicates a loss of communication e.g. with a device or
    controller
    """

    pass


class Cycle_Alarm(Alarm):
    """
    An alarm that indicates off-normal conditions associated with HVAC
    cycles
    """

    pass


class Short_Cycle_Alarm(Cycle_Alarm):
    """
    An alarm that indicates a short cycle occurred. A short cycle occurs
    when a cooling cycle is prevented from completing its full cycle
    """

    pass


class Emergency_Alarm(Alarm):
    """
    Alarms that indicate off-normal conditions associated with emergency
    systems
    """

    pass


class Emergency_Generator_Alarm(Emergency_Alarm):
    """
    An alarm that indicates off-normal conditions associated with an
    emergency generator
    """

    pass


class Failure_Alarm(Alarm):
    """
    Alarms that indicate the failure of devices, equipment, systems and
    control loops
    """

    pass


class Sensor_Failure_Alarm(Failure_Alarm):
    pass


class Unit_Failure_Alarm(Failure_Alarm):
    """
    An alarm that indicates the failure of an equipment or device
    """

    pass


class Humidity_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    concentration of water vapor in the air.
    """

    pass


class High_Humidity_Alarm(Humidity_Alarm):
    """
    An alarm that indicates high concentration of water vapor in the air.
    """

    pass


class Low_Humidity_Alarm(Humidity_Alarm):
    """
    An alarm that indicates low concentration of water vapor in the air.
    """

    pass


class Leak_Alarm(Alarm):
    """
    An alarm that indicates leaks occured in systems containing fluids
    """

    pass


class Condensate_Leak_Alarm(Leak_Alarm):
    """
    An alarm that indicates a leak of condensate from a cooling system
    """

    pass


class Liquid_Detection_Alarm(Alarm):
    pass


class Low_Battery_Alarm(Alarm):
    """
    An alarm that indicates the battery is low.
    """

    pass


class Luminance_Alarm(Alarm):
    pass


class Maintenance_Required_Alarm(Alarm):
    """
    An alarm that indicates that repair/maintenance is required on an
    associated device or equipment
    """

    pass


class Overload_Alarm(Alarm):
    """
    An alarm that can indicate when a full-load current is exceeded.
    """

    pass


class Power_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    electrical power.
    """

    pass


class Power_Loss_Alarm(Power_Alarm):
    """
    An alarm that indicates a power failure.
    """

    pass


class Pressure_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    pressure.
    """

    pass


class High_Head_Pressure_Alarm(Pressure_Alarm):
    """
    An alarm that indicates a high pressure generated on the output side
    of a gas compressor in a refrigeration or air conditioning system.
    """

    pass


class Low_Suction_Pressure_Alarm(Pressure_Alarm):
    """
    An alarm that indicates a low suction pressure in the compressor in a
    refrigeration or air conditioning system.
    """

    pass


class Smoke_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    smoke.
    """

    pass


class Smoke_Detection_Alarm(Smoke_Alarm):
    pass


class Discharge_Air_Smoke_Detection_Alarm(Smoke_Detection_Alarm, Air_Alarm):
    pass


class Supply_Air_Smoke_Detection_Alarm(Smoke_Detection_Alarm, Air_Alarm):
    pass


class Temperature_Alarm(Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    temperature.
    """

    pass


class Air_Temperature_Alarm(Temperature_Alarm, Air_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    temperature of air.
    """

    pass


class Discharge_Air_Temperature_Alarm(Air_Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    temperature of discharge air.
    """

    pass


class Return_Air_Temperature_Alarm(Air_Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    temperature of return air.
    """

    pass


class Supply_Air_Temperature_Alarm(Air_Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with the
    temperature of supply air.
    """

    pass


class High_Temperature_Alarm(Temperature_Alarm):
    """
    An alarm that indicates high temperature.
    """

    pass


class High_Discharge_Air_Temperature_Alarm(
    Supply_Air_Temperature_Alarm, High_Temperature_Alarm
):
    """
    An alarm that indicates that discharge air temperature is too high
    """

    pass


class High_Return_Air_Temperature_Alarm(
    Return_Air_Temperature_Alarm, High_Temperature_Alarm
):
    """
    An alarm that indicates that return air temperature is too high
    """

    pass


class High_Supply_Air_Temperature_Alarm(
    Supply_Air_Temperature_Alarm, High_Temperature_Alarm
):
    pass


class Low_Temperature_Alarm(Temperature_Alarm):
    """
    An alarm that indicates low temperature.
    """

    pass


class Low_Discharge_Air_Temperature_Alarm(
    Supply_Air_Temperature_Alarm, Low_Temperature_Alarm
):
    pass


class Low_Return_Air_Temperature_Alarm(
    Return_Air_Temperature_Alarm, Low_Temperature_Alarm
):
    """
    An alarm that indicates that return air temperature is too low
    """

    pass


class Low_Supply_Air_Temperature_Alarm(
    Supply_Air_Temperature_Alarm, Low_Temperature_Alarm
):
    pass


class Valve_Position_Alarm(Alarm):
    """
    An alarm that indicates that the valve position is not in a normal
    state.
    """

    pass


class Voltage_Alarm(Alarm):
    """
    An alarm that indicates the voltage is not in a normal state.
    """

    pass


class Low_Voltage_Alarm(Voltage_Alarm):
    """
    An alarm that indicates the voltage is lower than its normal state.
    """

    pass


class Water_Alarm(Alarm):
    """
    Alarm that indicates an undesirable event with a pipe, container, or
    equipment carrying water e.g. water leak
    """

    pass


class Deionized_Water_Alarm(Water_Alarm):
    """
    An alarm that indicates deionized water leaks.
    """

    pass


class No_Water_Alarm(Water_Alarm):
    """
    Alarm indicating that there is no water in the equipment or system
    """

    pass


class Water_Level_Alarm(Water_Alarm):
    """
    An alarm that indicates a high or low water level e.g. in a basin
    """

    pass


class Collection_Basin_Water_Level_Alarm(Water_Level_Alarm):
    """
    An alarm that indicates a high or low level of water in the collection
    basin, e.g. within a Cooling_Tower
    """

    pass


class Max_Water_Level_Alarm(Water_Level_Alarm):
    """
    Alarm indicating that the maximum water level was reached
    """

    pass


class Min_Water_Level_Alarm(Water_Level_Alarm):
    """
    Alarm indicating that the minimum water level was reached
    """

    pass


class Water_Loss_Alarm(Water_Alarm):
    """
    An alarm that indicates a loss of water e.g. during transport
    """

    pass


class Water_Temperature_Alarm(Water_Alarm, Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    temperature of water.
    """

    pass


class Entering_Water_Temperature_Alarm(Water_Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    temperature of the entering water.
    """

    pass


class Leaving_Water_Temperature_Alarm(Water_Temperature_Alarm):
    """
    An alarm that indicates the off-normal conditions associated with
    temperature of the leaving water.
    """

    pass


class Command(Point):
    """
    A Command is an output point that directly determines the behavior of
    equipment and/or affects relevant operational points.
    """

    pass


class Boiler_Command(Command):
    """
    A command to control a boiler
    """

    pass


class Bypass_Command(Command):
    pass


class Cooling_Command(Command):
    """
    Controls the amount of cooling to be delivered (typically as a
    proportion of total cooling output)
    """

    pass


class Damper_Command(Command):
    """
    Controls properties of dampers
    """

    pass


class Dehumidify_Command(Command):
    """
    Triggers the dehumidification process, actively removing moisture from
    the air to achieve desired humidity levels
    """

    pass


class Direction_Command(Command):
    """
    Commands that affect the direction of some phenomenon
    """

    pass


class Disable_Command(Command):
    """
    Commands that disable functionality
    """

    pass


class Disable_Differential_Enthalpy_Command(Disable_Command):
    """
    Disables the use of differential enthalpy control
    """

    pass


class Disable_Differential_Temperature_Command(Disable_Command):
    """
    Disables the use of differential temperature control
    """

    pass


class Disable_Fixed_Enthalpy_Command(Disable_Command):
    """
    Disables the use of fixed enthalpy control
    """

    pass


class Disable_Fixed_Temperature_Command(Disable_Command):
    """
    Disables the use of fixed temperature temperature
    """

    pass


class Enable_Command(Command):
    """
    Commands that enable functionality
    """

    pass


class Cooling_Enable_Command(Enable_Command):
    """
    Command that enables cooling functionality in equipment but certain
    condition(s) must be met first before actively cooling. For the
    actively cooling control, see Cooling_Command.
    """

    pass


class Enable_Differential_Enthalpy_Command(Enable_Command):
    """
    Enables the use of differential enthalpy control
    """

    pass


class Enable_Differential_Temperature_Command(Enable_Command):
    """
    Enables the use of differential temperature control
    """

    pass


class Enable_Fixed_Enthalpy_Command(Enable_Command):
    """
    Enables the use of fixed enthalpy control
    """

    pass


class Enable_Fixed_Temperature_Command(Enable_Command):
    """
    Enables the use of fixed temperature control
    """

    pass


class Heating_Enable_Command(Enable_Command):
    """
    Command that enables heating functionality in equipment but certain
    condition(s) must be met first before actively heating. For the
    actively heating control, see Heating_Command.
    """

    pass


class Run_Enable_Command(Enable_Command):
    pass


class Stage_Enable_Command(Enable_Command):
    """
    A point representing a discrete stage which the equipment should be
    operating at. The desired stage number should be identified by an
    entity property
    """

    pass


class System_Enable_Command(Enable_Command):
    """
    Enables operation of a system
    """

    pass


class Chilled_Water_System_Enable_Command(System_Enable_Command):
    """
    Enables operation of the chilled water system
    """

    pass


class Hot_Water_System_Enable_Command(System_Enable_Command):
    """
    Enables operation of the hot water system
    """

    pass


class Domestic_Hot_Water_System_Enable_Command(Hot_Water_System_Enable_Command):
    """
    Enables operation of the domestic hot water system
    """

    pass


class VFD_Enable_Command(Enable_Command):
    """
    Enables operation of a variable frequency drive
    """

    pass


class Exhaust_Fan_Disable_Command(Command):
    pass


class Fan_Command(Command):
    """
    Controls properties of fans
    """

    pass


class Fan_Speed_Command(Fan_Command):
    """
    Controls the speed of fans
    """

    pass


class Frequency_Command(Command):
    """
    Controls the frequency of a device's operation (e.g. rotational
    frequency)
    """

    pass


class Max_Frequency_Command(Frequency_Command):
    """
    Sets the maximum permitted frequency
    """

    pass


class Min_Frequency_Command(Frequency_Command):
    pass


class Heating_Command(Command):
    """
    Controls the amount of heating to be delivered (typically as a
    proportion of total heating output)
    """

    pass


class Humidify_Command(Command):
    pass


class Lead_Lag_Command(Command):
    """
    Enables lead/lag operation
    """

    pass


class Level_Command(Command):
    """
    Adjusts the operational state to a specific level within a predefined
    range.
    """

    pass


class Light_Command(Command):
    pass


class Lighting_Correlated_Color_Temperature_Command(Command):
    """
    A command to set correlated color temperature (CCT) which is the
    temperature of the Planckian radiator whose perceived color most
    closely resembles that of a given stimulus at the same brightness and
    under specified viewing conditions.
    """

    pass


class Lighting_Level_Command(Command):
    """
    Controls the amount of the light provided by the device typically in
    percentages.
    """

    pass


class Load_Shed_Command(Command):
    """
    Controls load shedding behavior provided by a control system
    """

    pass


class Occupied_Load_Shed_Command(Load_Shed_Command):
    pass


class Zone_Occupied_Load_Shed_Command(Occupied_Load_Shed_Command):
    pass


class Standby_Load_Shed_Command(Load_Shed_Command):
    pass


class Zone_Standby_Load_Shed_Command(Standby_Load_Shed_Command):
    pass


class Unoccupied_Load_Shed_Command(Load_Shed_Command):
    pass


class Zone_Unoccupied_Load_Shed_Command(Unoccupied_Load_Shed_Command):
    pass


class Luminance_Command(Command):
    """
    Controls the amount of luminance delivered by a lighting system
    """

    pass


class Mode_Command(Command):
    """
    Controls the operating mode of a device or controller
    """

    pass


class Automatic_Mode_Command(Mode_Command):
    """
    Controls whether or not a device or controller is operating in
    "Automatic" mode
    """

    pass


class Box_Mode_Command(Mode_Command):
    pass


class Maintenance_Mode_Command(Mode_Command):
    """
    Controls whether or not a device or controller is operating in
    "Maintenance" mode
    """

    pass


class Occupancy_Command(Command):
    """
    Controls whether or not a device or controller is operating in
    "Occupied" mode
    """

    pass


class On_Off_Command(Command):
    """
    An On/Off Command controls or reports the binary status of a control
    loop, relay or equipment activity
    """

    pass


class Lead_On_Off_Command(On_Off_Command):
    """
    Controls the active/inactive status of the "lead" part of a lead/lag
    system
    """

    pass


class Off_Command(On_Off_Command):
    """
    An Off Command controls or reports the binary 'off' status of a
    control loop, relay or equipment activity. It can only be used to
    stop/deactivate an associated equipment or process, or determine that
    the related entity is 'off'
    """

    pass


class On_Command(On_Off_Command):
    """
    An On Command controls or reports the binary 'on' status of a control
    loop, relay or equipment activity. It can only be used to
    start/activate an associated equipment or process, or determine that
    the related entity is 'on'
    """

    pass


class Open_Close_Command(On_Off_Command):
    """
    A binary signal given to a device, such as a damper or valve, to
    either open or close
    """

    pass


class Start_Stop_Command(On_Off_Command):
    """
    A Start/Stop Command controls or reports the active/inactive status of
    a control sequence
    """

    pass


class Steam_On_Off_Command(On_Off_Command):
    pass


class Override_Command(Command):
    """
    Controls or reports whether or not a device or control loop is in
    'override'
    """

    pass


class Curtailment_Override_Command(Override_Command):
    pass


class Position_Command(Command):
    """
    Controls or reports the position of some object
    """

    pass


class Damper_Position_Command(Position_Command, Damper_Command):
    """
    Controls the position (the degree of openness) of a damper
    """

    pass


class Preheat_Command(Command):
    """
    A command to activate preheating. Typically used to preheat cool air
    coming from a mixing box or economizer
    """

    pass


class Pump_Command(Command):
    """
    Controls or reports the speed of a pump (typically as a proportion of
    its full pumping capacity)
    """

    pass


class Reheat_Command(Command):
    """
    A command to activate reheating, which is used for either heating or
    for dehumidification purposes
    """

    pass


class Relay_Command(Command):
    """
    Commands to switch the relay
    """

    pass


class Reset_Command(Command):
    """
    Commands that reset a flag, property or value to its default
    """

    pass


class Fault_Reset_Command(Reset_Command):
    """
    Clears a fault status
    """

    pass


class Filter_Reset_Command(Reset_Command):
    pass


class Speed_Reset_Command(Reset_Command):
    pass


class Speed_Command(Command):
    """
    A command to set speed to a certain degree.
    """

    pass


class Tint_Command(Command):
    """
    The target level of window tint.
    """

    pass


class Valve_Command(Command):
    """
    Controls or reports the openness of a valve (typically as a proportion
    of its full range of motion)
    """

    pass


class Valve_Position_Command(Position_Command, Valve_Command):
    """
    Controls the position (the degree of openness) of a valve
    """

    pass


class Parameter(Point):
    """
    Parameter points are configuration settings used to guide the
    operation of equipment and control systems; for example they may
    provide bounds on valid setpoint values
    """

    pass


class Alarm_Sensitivity_Parameter(Parameter):
    """
    A parameter indicates the sensitivity to activate an alarm.
    """

    pass


class CO2_Alarm_Sensitivity_Parameter(Alarm_Sensitivity_Parameter):
    """
    A parameter indicates the sensitivity to activate a CO2 alarm.
    """

    pass


class Temperature_Alarm_Sensitivity_Parameter(Alarm_Sensitivity_Parameter):
    """
    A parameter indicates the sensitivity to activate a temperature alarm.
    """

    pass


class Delay_Parameter(Parameter):
    """
    A parameter determining how long to delay a subsequent action to take
    place after a received signal
    """

    pass


class Alarm_Delay_Parameter(Delay_Parameter):
    """
    A parameter determining how long to delay an alarm after sufficient
    conditions have been met
    """

    pass


class Humidity_Parameter(Parameter):
    """
    Parameters relevant to humidity-related systems and points
    """

    pass


class High_Humidity_Alarm_Parameter(Humidity_Parameter):
    """
    A parameter determining the humidity level at which to trigger a high
    humidity alarm
    """

    pass


class Low_Humidity_Alarm_Parameter(Humidity_Parameter):
    """
    A parameter determining the humidity level at which to trigger a low
    humidity alarm
    """

    pass


class Limit(Parameter):
    """
    A parameter that places an upper or lower bound on the range of
    permitted values of another point
    """

    pass


class Air_Flow_Setpoint_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Air_Flow_Setpoint.
    """

    pass


class Close_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Close_Setpoint.
    """

    pass


class Current_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Current_Setpoint.
    """

    pass


class Differential_Pressure_Setpoint_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Differential_Pressure_Setpoint.
    """

    pass


class Fresh_Air_Setpoint_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Fresh_Air_Setpoint.
    """

    pass


class Max_Limit(Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Setpoint.
    """

    pass


class Max_Air_Flow_Setpoint_Limit(Max_Limit, Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Air_Flow_Setpoint.
    """

    pass


class Max_Cooling_Discharge_Air_Flow_Setpoint_Limit(Max_Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Cooling_Supply_Air_Flow_Setpoint_Limit(Max_Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Occupied_Cooling_Discharge_Air_Flow_Setpoint_Limit(
    Max_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Occupied_Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Occupied_Cooling_Supply_Air_Flow_Setpoint_Limit(
    Max_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Occupied_Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Unoccupied_Cooling_Discharge_Air_Flow_Setpoint_Limit(
    Max_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Unoccupied_Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Unoccupied_Cooling_Supply_Air_Flow_Setpoint_Limit(
    Max_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Unoccupied_Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Heating_Discharge_Air_Flow_Setpoint_Limit(Max_Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Heating_Supply_Air_Flow_Setpoint_Limit(Max_Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Occupied_Heating_Discharge_Air_Flow_Setpoint_Limit(
    Max_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Occupied_Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Occupied_Heating_Supply_Air_Flow_Setpoint_Limit(
    Max_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Occupied_Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Unoccupied_Heating_Discharge_Air_Flow_Setpoint_Limit(
    Max_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Unoccupied_Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Max_Unoccupied_Heating_Supply_Air_Flow_Setpoint_Limit(
    Max_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Unoccupied_Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Max_Outside_Air_Flow_Setpoint_Limit(Max_Air_Flow_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Outside_Air_Flow_Setpoint.
    """

    pass


class Max_Chilled_Water_Differential_Pressure_Setpoint_Limit(
    Max_Limit, Differential_Pressure_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Chilled_Water_Differential_Pressure_Setpoint.
    """

    pass


class Max_Fresh_Air_Setpoint_Limit(Max_Limit, Fresh_Air_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Fresh_Air_Setpoint.
    """

    pass


class Max_Hot_Water_Differential_Pressure_Setpoint_Limit(
    Max_Limit, Differential_Pressure_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Hot_Water_Differential_Pressure_Setpoint.
    """

    pass


class Min_Limit(Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Setpoint.
    """

    pass


class Min_Air_Flow_Setpoint_Limit(Min_Limit, Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Air_Flow_Setpoint.
    """

    pass


class Min_Cooling_Discharge_Air_Flow_Setpoint_Limit(Min_Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Cooling_Supply_Air_Flow_Setpoint_Limit(Min_Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Occupied_Cooling_Discharge_Air_Flow_Setpoint_Limit(
    Min_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Occupied_Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Occupied_Cooling_Supply_Air_Flow_Setpoint_Limit(
    Min_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Occupied_Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Unoccupied_Cooling_Discharge_Air_Flow_Setpoint_Limit(
    Min_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Unoccupied_Cooling_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Unoccupied_Cooling_Supply_Air_Flow_Setpoint_Limit(
    Min_Cooling_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Unoccupied_Cooling_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Heating_Discharge_Air_Flow_Setpoint_Limit(Min_Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Heating_Supply_Air_Flow_Setpoint_Limit(Min_Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Occupied_Heating_Discharge_Air_Flow_Setpoint_Limit(
    Min_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Occupied_Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Occupied_Heating_Supply_Air_Flow_Setpoint_Limit(
    Min_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Occupied_Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Unoccupied_Heating_Discharge_Air_Flow_Setpoint_Limit(
    Min_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Unoccupied_Heating_Discharge_Air_Flow_Setpoint.
    """

    pass


class Min_Unoccupied_Heating_Supply_Air_Flow_Setpoint_Limit(
    Min_Heating_Supply_Air_Flow_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Unoccupied_Heating_Supply_Air_Flow_Setpoint.
    """

    pass


class Min_Outside_Air_Flow_Setpoint_Limit(Min_Air_Flow_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Outside_Air_Flow_Setpoint.
    """

    pass


class Min_Chilled_Water_Differential_Pressure_Setpoint_Limit(
    Min_Limit, Differential_Pressure_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Chilled_Water_Differential_Pressure_Setpoint.
    """

    pass


class Min_Fresh_Air_Setpoint_Limit(Min_Limit, Fresh_Air_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Fresh_Air_Setpoint.
    """

    pass


class Min_Hot_Water_Differential_Pressure_Setpoint_Limit(
    Min_Limit, Differential_Pressure_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Hot_Water_Differential_Pressure_Setpoint.
    """

    pass


class Position_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Position_Setpoint.
    """

    pass


class Max_Position_Setpoint_Limit(Max_Limit, Position_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Position_Setpoint.
    """

    pass


class Min_Position_Setpoint_Limit(Min_Limit, Position_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Position_Setpoint.
    """

    pass


class Speed_Setpoint_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Speed_Setpoint.
    """

    pass


class Max_Speed_Setpoint_Limit(Max_Limit, Speed_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Speed_Setpoint.
    """

    pass


class Min_Speed_Setpoint_Limit(Min_Limit, Speed_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Speed_Setpoint.
    """

    pass


class Static_Pressure_Setpoint_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Static_Pressure_Setpoint.
    """

    pass


class High_Static_Pressure_Cutout_Setpoint_Limit(Static_Pressure_Setpoint_Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a High_Static_Pressure_Cutout_Setpoint.
    """

    pass


class Max_Static_Pressure_Setpoint_Limit(Max_Limit, Static_Pressure_Setpoint_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Static_Pressure_Setpoint.
    """

    pass


class Max_Discharge_Air_Static_Pressure_Setpoint_Limit(
    Max_Static_Pressure_Setpoint_Limit, Max_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Discharge_Air_Static_Pressure_Setpoint.
    """

    pass


class Max_Supply_Air_Static_Pressure_Setpoint_Limit(
    Max_Static_Pressure_Setpoint_Limit, Max_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Supply_Air_Static_Pressure_Setpoint.
    """

    pass


class Min_Static_Pressure_Setpoint_Limit(Min_Limit, Static_Pressure_Setpoint_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Static_Pressure_Setpoint.
    """

    pass


class Min_Discharge_Air_Static_Pressure_Setpoint_Limit(
    Min_Static_Pressure_Setpoint_Limit, Min_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Discharge_Air_Static_Pressure_Setpoint.
    """

    pass


class Min_Supply_Air_Static_Pressure_Setpoint_Limit(
    Min_Static_Pressure_Setpoint_Limit, Min_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Supply_Air_Static_Pressure_Setpoint.
    """

    pass


class Ventilation_Air_Flow_Ratio_Limit(Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Ventilation_Air_Flow_Ratio_Setpoint.
    """

    pass


class Load_Parameter(Parameter):
    pass


class Max_Load_Setpoint(Load_Parameter):
    pass


class Min_Load_Setpoint(Load_Parameter):
    pass


class PID_Parameter(Parameter):
    pass


class Gain_Parameter(PID_Parameter):
    pass


class Derivative_Gain_Parameter(Gain_Parameter):
    pass


class Integral_Gain_Parameter(Gain_Parameter):
    pass


class Discharge_Air_Integral_Gain_Parameter(Integral_Gain_Parameter):
    pass


class Supply_Air_Integral_Gain_Parameter(Integral_Gain_Parameter):
    pass


class Proportional_Gain_Parameter(Gain_Parameter):
    pass


class Discharge_Air_Proportional_Gain_Parameter(Proportional_Gain_Parameter):
    pass


class Supply_Air_Proportional_Gain_Parameter(Proportional_Gain_Parameter):
    pass


class Proportional_Band_Parameter(PID_Parameter):
    pass


class Differential_Pressure_Proportional_Band(Proportional_Band_Parameter):
    pass


class Chilled_Water_Differential_Pressure_Proportional_Band_Parameter(
    Differential_Pressure_Proportional_Band
):
    pass


class Entering_Water_Differential_Pressure_Proportional_Band_Parameter(
    Differential_Pressure_Proportional_Band
):
    pass


class Hot_Water_Differential_Pressure_Proportional_Band_Parameter(
    Differential_Pressure_Proportional_Band
):
    pass


class Leaving_Water_Differential_Pressure_Proportional_Band_Parameter(
    Differential_Pressure_Proportional_Band
):
    pass


class Exhaust_Air_Flow_Proportional_Band_Parameter(Proportional_Band_Parameter):
    pass


class Exhaust_Air_Stack_Flow_Proportional_Band_Parameter(
    Exhaust_Air_Flow_Proportional_Band_Parameter
):
    pass


class Static_Pressure_Proportional_Band_Parameter(Proportional_Band_Parameter):
    pass


class Discharge_Air_Static_Pressure_Proportional_Band_Parameter(
    Static_Pressure_Proportional_Band_Parameter
):
    pass


class Exhaust_Air_Static_Pressure_Proportional_Band_Parameter(
    Static_Pressure_Proportional_Band_Parameter
):
    pass


class Supply_Air_Static_Pressure_Proportional_Band_Parameter(
    Static_Pressure_Proportional_Band_Parameter
):
    pass


class Step_Parameter(PID_Parameter):
    pass


class Differential_Pressure_Step_Parameter(Step_Parameter):
    pass


class Chilled_Water_Differential_Pressure_Step_Parameter(
    Differential_Pressure_Step_Parameter
):
    pass


class Static_Pressure_Step_Parameter(Step_Parameter):
    pass


class Air_Static_Pressure_Step_Parameter(Static_Pressure_Step_Parameter):
    pass


class Discharge_Air_Static_Pressure_Step_Parameter(Air_Static_Pressure_Step_Parameter):
    pass


class Supply_Air_Static_Pressure_Step_Parameter(Air_Static_Pressure_Step_Parameter):
    pass


class Time_Parameter(PID_Parameter):
    pass


class Derivative_Time_Parameter(Time_Parameter):
    pass


class Integral_Time_Parameter(Time_Parameter):
    pass


class Differential_Pressure_Integral_Time_Parameter(Integral_Time_Parameter):
    pass


class Chilled_Water_Differential_Pressure_Integral_Time_Parameter(
    Differential_Pressure_Integral_Time_Parameter
):
    pass


class Entering_Water_Differential_Pressure_Integral_Time_Parameter(
    Differential_Pressure_Integral_Time_Parameter
):
    pass


class Hot_Water_Differential_Pressure_Integral_Time_Parameter(
    Differential_Pressure_Integral_Time_Parameter
):
    pass


class Leaving_Water_Differential_Pressure_Integral_Time_Parameter(
    Differential_Pressure_Integral_Time_Parameter
):
    pass


class Exhaust_Air_Flow_Integral_Time_Parameter(Integral_Time_Parameter):
    pass


class Exhaust_Air_Stack_Flow_Integral_Time_Parameter(
    Exhaust_Air_Flow_Integral_Time_Parameter
):
    pass


class Static_Pressure_Integral_Time_Parameter(Integral_Time_Parameter):
    pass


class Discharge_Air_Static_Pressure_Integral_Time_Parameter(
    Static_Pressure_Integral_Time_Parameter
):
    pass


class Supply_Air_Static_Pressure_Integral_Time_Parameter(
    Static_Pressure_Integral_Time_Parameter
):
    pass


class Temperature_Parameter(Parameter):
    """
    Parameters relevant to temperature-related systems and points
    """

    pass


class Air_Temperature_Integral_Time_Parameter(
    Temperature_Parameter, Integral_Time_Parameter
):
    pass


class Cooling_Discharge_Air_Temperature_Integral_Time_Parameter(
    Air_Temperature_Integral_Time_Parameter
):
    pass


class Cooling_Supply_Air_Temperature_Integral_Time_Parameter(
    Air_Temperature_Integral_Time_Parameter
):
    pass


class Heating_Discharge_Air_Temperature_Integral_Time_Parameter(
    Air_Temperature_Integral_Time_Parameter
):
    pass


class Heating_Supply_Air_Temperature_Integral_Time_Parameter(
    Air_Temperature_Integral_Time_Parameter
):
    pass


class Air_Temperature_Setpoint_Limit(Temperature_Parameter, Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Air_Temperature_Setpoint.
    """

    pass


class Discharge_Air_Temperature_Setpoint_Limit(Air_Temperature_Setpoint_Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Discharge_Air_Temperature_Setpoint.
    """

    pass


class Supply_Air_Temperature_Setpoint_Limit(Air_Temperature_Setpoint_Limit):
    """
    A parameter that places a lower or upper bound on the range of
    permitted values of a Supply_Air_Temperature_Setpoint.
    """

    pass


class Discharge_Air_Temperature_Proportional_Band_Parameter(
    Proportional_Band_Parameter, Temperature_Parameter
):
    pass


class Entering_Water_Temperature_Integral_Time_Parameter(
    Temperature_Parameter, Integral_Time_Parameter
):
    pass


class Entering_Water_Temperature_Proportional_Band_Parameter(
    Proportional_Band_Parameter, Temperature_Parameter
):
    pass


class High_Temperature_Alarm_Parameter(Temperature_Parameter):
    """
    A parameter determining the temperature level at which to trigger a
    high temperature alarm
    """

    pass


class Leaving_Water_Temperature_Integral_Time_Parameter(
    Temperature_Parameter, Integral_Time_Parameter
):
    pass


class Leaving_Water_Temperature_Proportional_Band_Parameter(
    Proportional_Band_Parameter, Temperature_Parameter
):
    pass


class Lockout_Temperature_Differential_Parameter(Temperature_Parameter):
    pass


class Outside_Air_Lockout_Temperature_Differential_Parameter(
    Lockout_Temperature_Differential_Parameter
):
    pass


class High_Outside_Air_Lockout_Temperature_Differential_Parameter(
    Outside_Air_Lockout_Temperature_Differential_Parameter
):
    """
    The upper bound of the outside air temperature lockout range
    """

    pass


class Low_Outside_Air_Lockout_Temperature_Differential_Parameter(
    Outside_Air_Lockout_Temperature_Differential_Parameter
):
    """
    The lower bound of the outside air temperature lockout range
    """

    pass


class Low_Freeze_Protect_Temperature_Parameter(Temperature_Parameter):
    pass


class Low_Temperature_Alarm_Parameter(Temperature_Parameter):
    """
    A parameter determining the temperature level at which to trigger a
    low temperature alarm
    """

    pass


class Max_Temperature_Setpoint_Limit(Temperature_Parameter, Max_Limit):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Temperature_Setpoint.
    """

    pass


class Max_Discharge_Air_Temperature_Setpoint_Limit(
    Supply_Air_Temperature_Setpoint_Limit, Max_Temperature_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Discharge_Air_Temperature_Setpoint.
    """

    pass


class Max_Supply_Air_Temperature_Setpoint_Limit(
    Supply_Air_Temperature_Setpoint_Limit, Max_Temperature_Setpoint_Limit
):
    """
    A parameter that places an upper bound on the range of permitted
    values of a Supply_Air_Temperature_Setpoint.
    """

    pass


class Min_Temperature_Setpoint_Limit(Temperature_Parameter, Min_Limit):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Temperature_Setpoint.
    """

    pass


class Min_Discharge_Air_Temperature_Setpoint_Limit(
    Supply_Air_Temperature_Setpoint_Limit, Min_Temperature_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Discharge_Air_Temperature_Setpoint.
    """

    pass


class Min_Supply_Air_Temperature_Setpoint_Limit(
    Supply_Air_Temperature_Setpoint_Limit, Min_Temperature_Setpoint_Limit
):
    """
    A parameter that places a lower bound on the range of permitted values
    of a Supply_Air_Temperature_Setpoint.
    """

    pass


class Supply_Air_Temperature_Proportional_Band_Parameter(
    Proportional_Band_Parameter, Temperature_Parameter
):
    pass


class Cooling_Discharge_Air_Temperature_Proportional_Band_Parameter(
    Supply_Air_Temperature_Proportional_Band_Parameter
):
    pass


class Cooling_Supply_Air_Temperature_Proportional_Band_Parameter(
    Supply_Air_Temperature_Proportional_Band_Parameter
):
    pass


class Heating_Discharge_Air_Temperature_Proportional_Band_Parameter(
    Supply_Air_Temperature_Proportional_Band_Parameter
):
    pass


class Heating_Supply_Air_Temperature_Proportional_Band_Parameter(
    Supply_Air_Temperature_Proportional_Band_Parameter
):
    pass


class Temperature_Step_Parameter(Temperature_Parameter, Step_Parameter):
    pass


class Air_Temperature_Step_Parameter(Temperature_Step_Parameter):
    pass


class Discharge_Air_Temperature_Step_Parameter(Air_Temperature_Step_Parameter):
    pass


class Supply_Air_Temperature_Step_Parameter(Air_Temperature_Step_Parameter):
    pass


class Tolerance_Parameter(Parameter):
    """
    difference between upper and lower limits of size for a given nominal
    dimension or value.
    """

    pass


class Humidity_Tolerance_Parameter(Tolerance_Parameter, Humidity_Parameter):
    """
    A parameter determining the difference between upper and lower limits
    of humidity.
    """

    pass


class Temperature_Tolerance_Parameter(Tolerance_Parameter, Temperature_Parameter):
    """
    A parameter determining the difference between upper and lower limits
    of temperature.
    """

    pass


class Sensor(Point, _Sensor):
    """
    A Sensor is an input point that represents the value of a device or
    instrument designed to detect and measure a variable (ASHRAE
    Dictionary).
    """

    pass


class Adjust_Sensor(Sensor):
    """
    Measures user-provided adjustment of some value
    """

    pass


class Temperature_Adjust_Sensor(Adjust_Sensor):
    """
    Measures user-provided adjustment of temperature
    """

    pass


class Warm_Cool_Adjust_Sensor(Adjust_Sensor):
    """
    User provided adjustment of zone temperature, typically in the range
    of +/- 5 degrees
    """

    pass


class Air_Grains_Sensor(Sensor):
    """
    Measures the mass of water vapor in air
    """

    pass


class Outside_Air_Grains_Sensor(Air_Grains_Sensor):
    """
    Measures the mass of water vapor in outside air
    """

    pass


class Return_Air_Grains_Sensor(Air_Grains_Sensor):
    """
    Measures the mass of water vapor in return air
    """

    pass


class Air_Quality_Sensor(Sensor):
    """
    A sensor which provides a measure of air quality
    """

    pass


class Ammonia_Sensor(Air_Quality_Sensor):
    pass


class CO2_Sensor(Air_Quality_Sensor):
    """
    Measures properties of CO2 in air
    """

    pass


class CO2_Differential_Sensor(CO2_Sensor):
    """
    Measures the difference between CO2 levels of inside and outside air
    """

    pass


class CO2_Level_Sensor(CO2_Sensor):
    """
    Measures the concentration of CO2 in air
    """

    pass


class Zone_CO2_Level_Sensor(CO2_Level_Sensor):
    """
    A physical or virtual sensor which represents the CO2 level of an HVAC
    Zone
    """

    pass


class Outside_Air_CO2_Sensor(CO2_Sensor):
    """
    Measures the concentration of CO2 in outside air
    """

    pass


class Return_Air_CO2_Sensor(CO2_Sensor):
    """
    Measures the concentration of CO2 in return air
    """

    pass


class CO_Sensor(Air_Quality_Sensor):
    """
    Measures properties of CO
    """

    pass


class CO_Differential_Sensor(CO_Sensor):
    pass


class CO_Level_Sensor(CO_Sensor):
    """
    Measures the concentration of CO
    """

    pass


class Outside_Air_CO_Sensor(CO_Sensor):
    """
    Measures the concentration of CO in outside air
    """

    pass


class Return_Air_CO_Sensor(CO_Sensor):
    """
    Measures the concentration of CO in return air
    """

    pass


class Formaldehyde_Level_Sensor(Air_Quality_Sensor):
    """
    Measures the concentration of formaldehyde in air
    """

    pass


class Methane_Level_Sensor(Air_Quality_Sensor):
    """
    Measures the concentration of methane in air
    """

    pass


class NO2_Level_Sensor(Air_Quality_Sensor):
    """
    Measures the concentration of NO2 in air
    """

    pass


class Ozone_Level_Sensor(Air_Quality_Sensor):
    """
    Measures the concentration of ozone in air
    """

    pass


class Particulate_Matter_Sensor(Air_Quality_Sensor):
    """
    Detects pollutants in the ambient air
    """

    pass


class PM10_Sensor(Particulate_Matter_Sensor):
    """
    Detects matter of size 10 microns
    """

    pass


class PM10_Level_Sensor(PM10_Sensor):
    """
    Detects level of particulates of size 10 microns
    """

    pass


class PM1_Sensor(Particulate_Matter_Sensor):
    """
    Detects matter of size 1 micron
    """

    pass


class PM1_Level_Sensor(PM1_Sensor):
    """
    Detects level of particulates of size 1 microns
    """

    pass


class PM2_5_Sensor(Particulate_Matter_Sensor):
    """
    Detects matter of size 2.5 microns
    """

    _class_iri: URIRef = BRICK["PM2.5_Sensor"]
    pass


class PM2_5_Level_Sensor(PM2_5_Sensor):
    """
    Detects level of particulates of size 2.5 microns
    """

    _class_iri: URIRef = BRICK["PM2.5_Level_Sensor"]
    pass


class TVOC_Sensor(Particulate_Matter_Sensor):
    pass


class TVOC_Level_Sensor(TVOC_Sensor):
    """
    A sensor measuring the level of all VOCs in air
    """

    pass


class Radon_Concentration_Sensor(Air_Quality_Sensor):
    """
    Measures the concentration of radioactivity due to radon
    """

    pass


class Angle_Sensor(Sensor):
    """
    Measues the planar angle of some phenomenon
    """

    pass


class Solar_Azimuth_Angle_Sensor(Angle_Sensor):
    """
    Measures the azimuth angle of the sun
    """

    pass


class Solar_Zenith_Angle_Sensor(Angle_Sensor):
    """
    Measures the zenith angle of the sun
    """

    pass


class Capacity_Sensor(Sensor):
    pass


class Conductivity_Sensor(Sensor):
    """
    Measures electrical conductance
    """

    pass


class Deionised_Water_Conductivity_Sensor(Conductivity_Sensor):
    """
    Measures the electrical conductance of deionised water
    """

    pass


class Contact_Sensor(Sensor):
    """
    Senses or detects contact, such as for determining if a door is
    closed.
    """

    pass


class Current_Sensor(Sensor):
    """
    Senses the amperes of electrical current passing through the sensor
    """

    pass


class Current_Output_Sensor(Current_Sensor):
    """
    Senses the amperes of electrical current produced as output by a
    device
    """

    pass


class PV_Current_Output_Sensor(Current_Output_Sensor):
    """
    See Photovoltaic_Current_Output_Sensor
    """

    pass


class Photovoltaic_Current_Output_Sensor(Current_Output_Sensor):
    """
    Senses the amperes of electrical current produced as output by a
    photovoltaic device
    """

    pass


class Load_Current_Sensor(Current_Sensor):
    """
    Measures the current consumed by a load
    """

    pass


class Motor_Current_Sensor(Current_Sensor):
    """
    Measures the current consumed by a motor
    """

    pass


class Demand_Sensor(Sensor):
    """
    Measures the amount of power consumed by the use of some process;
    typically found by multiplying the tonnage of a unit (e.g. RTU) by the
    efficiency rating in kW/ton
    """

    pass


class Cooling_Demand_Sensor(Demand_Sensor):
    """
    Measures the amount of power consumed by a cooling process; typically
    found by multiplying the tonnage of a unit (e.g. RTU) by the
    efficiency rating in kW/ton
    """

    pass


class Average_Cooling_Demand_Sensor(Cooling_Demand_Sensor):
    """
    Measures the average power consumed by a cooling process as the amount
    of power consumed over some interval
    """

    pass


class Heating_Demand_Sensor(Demand_Sensor):
    """
    Measures the amount of power consumed by a heating process; typically
    found by multiplying the tonnage of a unit (e.g. RTU) by the
    efficiency rating in kW/ton
    """

    pass


class Average_Heating_Demand_Sensor(Heating_Demand_Sensor):
    """
    Measures the average power consumed by a heating process as the amount
    of power consumed over some interval
    """

    pass


class Peak_Demand_Sensor(Demand_Sensor):
    """
    The peak power consumed by a process over some period of time
    """

    pass


class Dewpoint_Sensor(Sensor):
    """
    Senses the dewpoint temperature . Dew point is the temperature to
    which air must be cooled to become saturated with water vapor
    """

    pass


class Discharge_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    """
    Measures dewpoint of discharge air
    """

    pass


class Exhaust_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    """
    Measures dewpoint of exhaust air
    """

    pass


class Outside_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    """
    Senses the dewpoint temperature of outside air
    """

    pass


class Return_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    """
    Senses the dewpoint temperature of return air
    """

    pass


class Supply_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    pass


class Zone_Air_Dewpoint_Sensor(Dewpoint_Sensor):
    """
    Measures dewpoint of zone air
    """

    pass


class Direction_Sensor(Sensor):
    """
    Measures the direction in degrees in which a phenomenon is occuring
    """

    pass


class Wind_Direction_Sensor(Direction_Sensor):
    """
    Measures the direction of wind in degrees relative to North
    """

    pass


class Duration_Sensor(Sensor):
    """
    Measures the duration of a phenomenon or event
    """

    pass


class On_Timer_Sensor(Duration_Sensor):
    """
    Measures the duration for which a device was in an active or "on"
    state
    """

    pass


class Rain_Duration_Sensor(Duration_Sensor):
    """
    Measures the duration of precipitation within some time frame
    """

    pass


class Run_Time_Sensor(Duration_Sensor):
    """
    Measures the duration for which a device was in an active or "on"
    state
    """

    pass


class Energy_Sensor(Sensor):
    """
    Measures energy consumption
    """

    pass


class Electric_Energy_Sensor(Energy_Sensor):
    pass


class Reactive_Energy_Sensor(Electric_Energy_Sensor):
    """
    Measures the integral of reactive power
    """

    pass


class Enthalpy_Sensor(Sensor):
    """
    Measures the total heat content of some substance
    """

    pass


class Air_Enthalpy_Sensor(Enthalpy_Sensor):
    """
    Measures the total heat content of air
    """

    pass


class Outside_Air_Enthalpy_Sensor(Air_Enthalpy_Sensor):
    """
    Measures the total heat content of outside air
    """

    pass


class Return_Air_Enthalpy_Sensor(Air_Enthalpy_Sensor):
    """
    Measures the total heat content of return air
    """

    pass


class Fire_Sensor(Sensor):
    """
    Measures the presence of fire
    """

    pass


class Flow_Sensor(Sensor):
    """
    Measures the rate of flow of some substance
    """

    pass


class Air_Flow_Sensor(Flow_Sensor):
    """
    Measures the rate of flow of air
    """

    pass


class Bypass_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of bypass air
    """

    pass


class Discharge_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of discharge air
    """

    pass


class Exhaust_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of exhaust air
    """

    pass


class Exhaust_Air_Stack_Flow_Sensor(Exhaust_Air_Flow_Sensor):
    """
    Measures the rate of flow of air in the exhaust air stack
    """

    pass


class Fume_Hood_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of air in a fume hood
    """

    pass


class Mixed_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of mixed air
    """

    pass


class Outside_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of outside air into the system
    """

    pass


class Return_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of return air
    """

    pass


class Supply_Air_Flow_Sensor(Air_Flow_Sensor):
    """
    Measures the rate of flow of supply air
    """

    pass


class Average_Discharge_Air_Flow_Sensor(Supply_Air_Flow_Sensor):
    """
    The computed average flow of discharge air over some interval
    """

    pass


class Average_Supply_Air_Flow_Sensor(Supply_Air_Flow_Sensor):
    """
    The computed average flow of supply air over some interval
    """

    pass


class Natural_Gas_Flow_Sensor(Flow_Sensor):
    """
    Measures the rate of flow of natural gas
    """

    pass


class Water_Flow_Sensor(Flow_Sensor):
    """
    Measures the rate of flow of water
    """

    pass


class Bypass_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the rate of flow of bypass water
    """

    pass


class Chilled_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the rate of flow in a chilled water circuit
    """

    pass


class Condenser_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the flow of the condenser water
    """

    pass


class Discharge_Water_Flow_Sensor(Water_Flow_Sensor):
    pass


class Chilled_Water_Discharge_Flow_Sensor(
    Chilled_Water_Flow_Sensor, Discharge_Water_Flow_Sensor
):
    pass


class Discharge_Condenser_Water_Flow_Sensor(
    Condenser_Water_Flow_Sensor, Discharge_Water_Flow_Sensor
):
    pass


class Entering_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the rate of flow of water entering a piece of equipment or
    system
    """

    pass


class Entering_Chilled_Water_Flow_Sensor(
    Chilled_Water_Flow_Sensor, Entering_Water_Flow_Sensor
):
    """
    Measures the rate of flow of chilled entering water
    """

    pass


class Entering_Condenser_Water_Flow_Sensor(Entering_Water_Flow_Sensor):
    """
    Measures the flow of the entering condenser water
    """

    pass


class Hot_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the rate of flow in a hot water circuit
    """

    pass


class Entering_Hot_Water_Flow_Sensor(Hot_Water_Flow_Sensor, Entering_Water_Flow_Sensor):
    """
    Measures the rate of flow of hot entering water
    """

    pass


class Hot_Water_Discharge_Flow_Sensor(
    Hot_Water_Flow_Sensor, Discharge_Water_Flow_Sensor
):
    pass


class Leaving_Water_Flow_Sensor(Water_Flow_Sensor):
    """
    Measures the rate of flow of water that is leaving a piece of
    equipment or system
    """

    pass


class Leaving_Chilled_Water_Flow_Sensor(
    Leaving_Water_Flow_Sensor, Chilled_Water_Flow_Sensor
):
    """
    Measures the rate of flow of chilled leaving water
    """

    pass


class Leaving_Condenser_Water_Flow_Sensor(
    Leaving_Water_Flow_Sensor, Condenser_Water_Flow_Sensor
):
    """
    Measures the flow of the leaving condenser water
    """

    pass


class Leaving_Hot_Water_Flow_Sensor(Leaving_Water_Flow_Sensor, Hot_Water_Flow_Sensor):
    """
    Measures the rate of flow of hot leaving water
    """

    pass


class Return_Water_Flow_Sensor(Water_Flow_Sensor):
    pass


class Chilled_Water_Return_Flow_Sensor(
    Chilled_Water_Flow_Sensor, Return_Water_Flow_Sensor
):
    pass


class Hot_Water_Return_Flow_Sensor(Hot_Water_Flow_Sensor, Return_Water_Flow_Sensor):
    pass


class Return_Condenser_Water_Flow_Sensor(
    Condenser_Water_Flow_Sensor, Return_Water_Flow_Sensor
):
    pass


class Supply_Water_Flow_Sensor(Water_Flow_Sensor):
    pass


class Chilled_Water_Supply_Flow_Sensor(
    Chilled_Water_Flow_Sensor, Supply_Water_Flow_Sensor
):
    pass


class Hot_Water_Supply_Flow_Sensor(Hot_Water_Flow_Sensor, Supply_Water_Flow_Sensor):
    pass


class Supply_Condenser_Water_Flow_Sensor(
    Condenser_Water_Flow_Sensor, Supply_Water_Flow_Sensor
):
    pass


class Frequency_Sensor(Sensor):
    """
    Measures the frequency of a phenomenon or aspect of a phenomenon, e.g.
    the frequency of a fan turning
    """

    pass


class Output_Frequency_Sensor(Frequency_Sensor):
    pass


class Gas_Sensor(Sensor):
    """
    Measures gas concentration (other than CO2)
    """

    pass


class Generation_Sensor(Sensor):
    """
    A sensor measuring how much something has been generated.
    """

    pass


class Energy_Generation_Sensor(Generation_Sensor):
    """
    A sensor measuring the amount of generated energy.
    """

    pass


class Hail_Sensor(Sensor):
    """
    Measures hail in terms of its size and damage potential
    """

    pass


class Heat_Sensor(Sensor):
    pass


class Humidity_Sensor(Sensor):
    """
    Measures the concentration of water vapor in air
    """

    pass


class Absolute_Humidity_Sensor(Humidity_Sensor):
    """
    Measures the present state of absolute humidity
    """

    pass


class Relative_Humidity_Sensor(Humidity_Sensor):
    """
    Measures the present state of absolute humidity relative to a maximum
    humidity given the same temperature
    """

    pass


class Discharge_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of discharge air
    """

    pass


class Exhaust_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of exhaust air
    """

    pass


class Mixed_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the humidity of mixed air
    """

    pass


class Outside_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of outside air
    """

    pass


class Return_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of return air
    """

    pass


class Supply_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of supply air
    """

    pass


class Zone_Air_Humidity_Sensor(Relative_Humidity_Sensor):
    """
    Measures the relative humidity of zone air
    """

    pass


class Illuminance_Sensor(Sensor):
    """
    Measures the total luminous flux incident on a surface, per unit area
    """

    pass


class Outside_Illuminance_Sensor(Illuminance_Sensor):
    """
    Measures the total luminous flux incident on an outside, per unit area
    """

    pass


class Imbalance_Sensor(Sensor):
    """
    A sensor which measures difference (imbalance) between phases of an
    electrical system
    """

    pass


class Current_Imbalance_Sensor(Imbalance_Sensor):
    """
    A sensor which measures the current difference (imbalance) between
    phases of an electrical system
    """

    pass


class Voltage_Imbalance_Sensor(Imbalance_Sensor):
    """
    A sensor which measures the voltage difference (imbalance) between
    phases of an electrical system
    """

    pass


class Lighting_Correlated_Color_Temperature_Sensor(Sensor):
    """
    A sensor to measure correlated color temperature (CCT) which is the
    temperature of the Planckian radiator whose perceived color most
    closely resembles that of a given stimulus at the same brightness and
    under specified viewing conditions.
    """

    pass


class Luminance_Sensor(Sensor):
    """
    Measures the luminous intensity per unit area of light travelling in a
    given direction
    """

    pass


class Motion_Sensor(Sensor):
    """
    Detects the presence of motion in some area
    """

    pass


class PIR_Sensor(Motion_Sensor):
    """
    Detects the presense of motion in some area using the differential
    change in infrared intensity between two or more receptors
    """

    pass


class Occupancy_Count_Sensor(Sensor):
    """
    Sensors measuring the number of people in an area
    """

    pass


class Occupancy_Sensor(Sensor):
    """
    Detects occupancy of some space or area
    """

    pass


class Piezoelectric_Sensor(Sensor):
    """
    Senses changes pressure, acceleration, temperature, force or strain
    via the piezoelectric effect
    """

    pass


class Position_Sensor(Sensor):
    """
    Measures the current position of a component in terms of a fraction of
    its full range of motion
    """

    pass


class Damper_Position_Sensor(Position_Sensor):
    """
    Measures the current position of a damper in terms of the percent of
    fully open
    """

    pass


class Sash_Position_Sensor(Position_Sensor):
    """
    Measures the current position of a sash in terms of the percent of
    fully open
    """

    pass


class Valve_Position_Sensor(Position_Sensor):
    """
    Measures the current position of a valve in terms of the percent of
    fully open
    """

    pass


class Power_Factor_Sensor(Sensor):
    """
    Sensors measuring power Factor, under periodic conditions, is the
    ratio of the absolute value of the active power (P) to the apparent
    power (S).
    """

    pass


class Power_Sensor(Sensor):
    """
    Measures the amount of instantaneous power consumed
    """

    pass


class Electric_Power_Sensor(Power_Sensor):
    """
    Measures the amount of instantaneous electric power consumed
    """

    pass


class Active_Power_Sensor(Electric_Power_Sensor):
    """
    Measures the portion of power that, averaged over a complete cycle of
    the AC waveform, results in net transfer of energy in one direction
    """

    pass


class Reactive_Power_Sensor(Electric_Power_Sensor):
    """
    Measures the portion of power that, averaged over a complete cycle of
    the AC waveform, is due to stored energy which returns to the source
    in each cycle
    """

    pass


class Thermal_Power_Sensor(Power_Sensor):
    pass


class Heating_Thermal_Power_Sensor(Thermal_Power_Sensor):
    pass


class Pressure_Sensor(Sensor):
    """
    Measure the amount of force acting on a unit area
    """

    pass


class Air_Pressure_Sensor(Pressure_Sensor):
    """
    Measures the pressure of the surrounding air.
    """

    pass


class Differential_Pressure_Sensor(Pressure_Sensor):
    """
    Measures the difference between two applied pressures
    """

    pass


class Air_Differential_Pressure_Sensor(
    Differential_Pressure_Sensor, Air_Pressure_Sensor
):
    """
    Measures the difference in pressure between two regions of air
    """

    pass


class Discharge_Air_Differential_Pressure_Sensor(Air_Differential_Pressure_Sensor):
    pass


class Exhaust_Air_Differential_Pressure_Sensor(Air_Differential_Pressure_Sensor):
    """
    Measures the difference in pressure between an upstream and downstream
    of an air duct or other air conduit used to exhaust air from the
    building
    """

    pass


class Return_Air_Differential_Pressure_Sensor(Air_Differential_Pressure_Sensor):
    """
    Measures the difference in pressure between the return and supply side
    """

    pass


class Supply_Air_Differential_Pressure_Sensor(Air_Differential_Pressure_Sensor):
    """
    Measures the difference in pressure between an upstream and downstream
    of an air duct or other air conduit used to supply air into the
    building
    """

    pass


class Filter_Differential_Pressure_Sensor(Differential_Pressure_Sensor):
    """
    Measures the difference in pressure on either side of a filter
    """

    pass


class Filter_Air_Differential_Pressure_Sensor(
    Filter_Differential_Pressure_Sensor, Air_Differential_Pressure_Sensor
):
    """
    Measures the difference in air pressure before and after an air
    filter.
    """

    pass


class Water_Differential_Pressure_Sensor(Differential_Pressure_Sensor):
    """
    Measures the difference in water pressure between two points in a
    system.
    """

    pass


class Chilled_Water_Differential_Pressure_Sensor(Water_Differential_Pressure_Sensor):
    """
    Measures the difference in water pressure on either side of a chilled
    water valve
    """

    pass


class Filter_Water_Differential_Pressure_Sensor(
    Filter_Differential_Pressure_Sensor, Water_Differential_Pressure_Sensor
):
    """
    Measures the difference in water pressure before and after a water
    filter.
    """

    pass


class Hot_Water_Differential_Pressure_Sensor(Water_Differential_Pressure_Sensor):
    """
    Measures the difference in water pressure on either side of a hot
    water valve
    """

    pass


class Domestic_Hot_Water_Differential_Pressure_Sensor(
    Hot_Water_Differential_Pressure_Sensor
):
    """
    Measures the pressure difference in domestic hot water systems.
    """

    pass


class Medium_Temperature_Hot_Water_Differential_Pressure_Sensor(
    Hot_Water_Differential_Pressure_Sensor
):
    """
    Measures the difference in water pressure between sections of a medium
    temperature hot water system
    """

    pass


class Gauge_Pressure_Sensor(Pressure_Sensor):
    """
    Pressure sensor which is zero-referenced against ambient air pressure
    """

    pass


class Chilled_Water_Gauge_Pressure_Sensor(Gauge_Pressure_Sensor):
    """
    Sensor measuring the gauge pressure (zero-referenced against ambient
    air pressure) of chilled water
    """

    pass


class Hot_Water_Gauge_Pressure_Sensor(Gauge_Pressure_Sensor):
    """
    Sensor measuring the gauge pressure (zero-referenced against ambient
    air pressure) of hot water
    """

    pass


class Static_Pressure_Sensor(Pressure_Sensor):
    """
    Measures resistance to airflow in a heating and cooling system's
    components and duct work
    """

    pass


class Air_Static_Pressure_Sensor(Static_Pressure_Sensor):
    """
    Measures the pressure exerted by the air in a system, not influenced
    by its motion.
    """

    pass


class Building_Air_Static_Pressure_Sensor(Air_Static_Pressure_Sensor):
    """
    The static pressure of air within a building
    """

    pass


class Discharge_Air_Static_Pressure_Sensor(Air_Static_Pressure_Sensor):
    """
    The static pressure of air within discharge regions of an HVAC system
    """

    pass


class Exhaust_Air_Static_Pressure_Sensor(Air_Static_Pressure_Sensor):
    """
    The static pressure of air within exhaust regions of an HVAC system
    """

    pass


class Average_Exhaust_Air_Static_Pressure_Sensor(Exhaust_Air_Static_Pressure_Sensor):
    """
    The computed average static pressure of air in exhaust regions of an
    HVAC system over some period of time
    """

    pass


class Lowest_Exhaust_Air_Static_Pressure_Sensor(Exhaust_Air_Static_Pressure_Sensor):
    """
    The lowest observed static pressure of air in exhaust regions of an
    HVAC system over some period of time
    """

    pass


class Supply_Air_Static_Pressure_Sensor(Air_Static_Pressure_Sensor):
    """
    The static pressure of air within supply regions of an HVAC system
    """

    pass


class Underfloor_Air_Plenum_Static_Pressure_Sensor(Air_Static_Pressure_Sensor):
    """
    Measures the outward push of air against the plenum surfaces and used
    to measure the resistance when air moves through the plenum
    """

    pass


class Velocity_Pressure_Sensor(Pressure_Sensor):
    """
    Measures the difference between total pressure and static pressure
    """

    pass


class Air_Velocity_Pressure_Sensor(Velocity_Pressure_Sensor):
    """
    Measures the difference between total air pressure and static air
    pressure.
    """

    pass


class Discharge_Air_Velocity_Pressure_Sensor(Air_Velocity_Pressure_Sensor):
    pass


class Exhaust_Air_Velocity_Pressure_Sensor(Air_Velocity_Pressure_Sensor):
    pass


class Supply_Air_Velocity_Pressure_Sensor(Air_Velocity_Pressure_Sensor):
    pass


class Water_Pressure_Sensor(Pressure_Sensor):
    """
    Measures the pressure exerted by water in a system.
    """

    pass


class Entering_Water_Pressure_Sensor(Water_Pressure_Sensor):
    """
    Measures the water pressure at the entry point of a system.
    """

    pass


class Leaving_Water_Pressure_Sensor(Water_Pressure_Sensor):
    """
    Measures the water pressure at the exit point of a system.
    """

    pass


class Rain_Level_Sensor(Sensor):
    """
    Measures the amount of precipitation fallen
    """

    pass


class Refrigerant_Level_Sensor(Sensor):
    pass


class Solar_Irradiance_Sensor(Sensor):
    """
    Measures solar irradiance levels for photovoltaic systems
    """

    pass


class Solar_Radiance_Sensor(Sensor):
    pass


class Speed_Sensor(Sensor):
    """
    Measures the magnitude of velocity of some form of movement
    """

    pass


class Differential_Speed_Sensor(Speed_Sensor):
    pass


class Motor_Speed_Sensor(Speed_Sensor):
    pass


class Wind_Speed_Sensor(Speed_Sensor):
    """
    Measured speed of wind, caused by air moving from high to low pressure
    """

    pass


class Temperature_Sensor(Sensor):
    """
    Measures temperature: the physical property of matter that
    quantitatively expresses the common notions of hot and cold
    """

    pass


class Air_Temperature_Sensor(Temperature_Sensor, _AirTemperatureSensor):
    """
    Measures the temperature of air
    """

    pass


class Air_Wet_Bulb_Temperature_Sensor(Air_Temperature_Sensor, Temperature_Sensor):
    pass


class Discharge_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of discharge air
    """

    pass


class Exhaust_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of exhaust air
    """

    pass


class Mixed_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of mixed air
    """

    pass


class Outside_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of outside air
    """

    pass


class Intake_Air_Temperature_Sensor(Outside_Air_Temperature_Sensor):
    """
    Measures air at the interface between the building and the outside
    """

    pass


class Outside_Air_Temperature_Enable_Differential_Sensor(
    Outside_Air_Temperature_Sensor
):
    pass


class Low_Outside_Air_Temperature_Enable_Differential_Sensor(
    Outside_Air_Temperature_Enable_Differential_Sensor
):
    pass


class Outside_Air_Wet_Bulb_Temperature_Sensor(
    Outside_Air_Temperature_Sensor, Air_Wet_Bulb_Temperature_Sensor
):
    """
    A sensor measuring the wet-bulb temperature of outside air
    """

    pass


class Return_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of return air
    """

    pass


class Room_Air_Temperature_Sensor(Air_Temperature_Sensor):
    pass


class Supply_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of supply air
    """

    pass


class Preheat_Discharge_Air_Temperature_Sensor(Supply_Air_Temperature_Sensor):
    """
    Measures the temperature of discharge air before heating is applied
    """

    pass


class Preheat_Supply_Air_Temperature_Sensor(Supply_Air_Temperature_Sensor):
    """
    Measures the temperature of supply air before it is heated
    """

    pass


class Underfloor_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    Measures the temperature of underfloor air
    """

    pass


class Zone_Air_Temperature_Sensor(Air_Temperature_Sensor):
    """
    A physical or virtual sensor which represents the temperature of an
    HVAC Zone
    """

    pass


class Average_Zone_Air_Temperature_Sensor(Zone_Air_Temperature_Sensor):
    """
    The computed average temperature of air in a zone, over some period of
    time
    """

    pass


class Coldest_Zone_Air_Temperature_Sensor(Zone_Air_Temperature_Sensor):
    """
    The zone temperature that is coldest; drives the supply temperature of
    hot air. A computed value rather than a physical sensor. Also referred
    to as a 'Lowest Zone Air Temperature Sensor'
    """

    pass


class Warmest_Zone_Air_Temperature_Sensor(Zone_Air_Temperature_Sensor):
    """
    The zone temperature that is warmest; drives the supply temperature of
    cold air. A computed value rather than a physical sensor. Also
    referred to as a 'Highest Zone Air Temperature Sensor'
    """

    pass


class Frost_Sensor(Temperature_Sensor, Sensor):
    """
    Senses the presence of frost or conditions that may cause frost
    """

    pass


class Heat_Sink_Temperature_Sensor(Temperature_Sensor):
    """
    Measure temperature of the heat sink on a device such as a VFD.
    """

    pass


class Natural_Gas_Temperature_Sensor(Temperature_Sensor):
    """
    Measures the temperature of natural gas
    """

    pass


class Radiant_Panel_Temperature_Sensor(Temperature_Sensor):
    """
    Measures the temperature of the radiant panel of the radiant heating
    and cooling HVAC system.
    """

    pass


class Embedded_Temperature_Sensor(Radiant_Panel_Temperature_Sensor):
    """
    Measures the internal temperature of the radiant layer of the radiant
    heating and cooling HVAC system.
    """

    pass


class Core_Temperature_Sensor(Embedded_Temperature_Sensor):
    """
    Measures the internal temperature of the radiant layer at the heat
    source or sink level of the radiant heating and cooling HVAC system.
    """

    pass


class Inside_Face_Surface_Temperature_Sensor(Radiant_Panel_Temperature_Sensor):
    """
    Measures the inside surface (relative to the space) of the radiant
    panel of the radiant heating and cooling HVAC system.
    """

    pass


class Outside_Face_Surface_Temperature_Sensor(Radiant_Panel_Temperature_Sensor):
    """
    Measures the outside surface (relative to the space) of the radiant
    panel of a radiant heating and cooling HVAC system.
    """

    pass


class Soil_Temperature_Sensor(Temperature_Sensor):
    """
    Measures the temperature of soil
    """

    pass


class Water_Temperature_Sensor(Temperature_Sensor):
    """
    Measures the temperature of water
    """

    pass


class Chilled_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of chilled water
    """

    pass


class Differential_Entering_Leaving_Water_Temperature_Sensor(
    Chilled_Water_Temperature_Sensor
):
    """
    Measures the difference in temperature between entering and leaving
    water of water a circuit
    """

    pass


class Entering_Chilled_Water_Temperature_Sensor(Chilled_Water_Temperature_Sensor):
    """
    Measures the temperature of chilled water that is enteringed to a
    cooling tower
    """

    pass


class Leaving_Chilled_Water_Temperature_Sensor(Chilled_Water_Temperature_Sensor):
    """
    Measures the temperature of chilled water that is supplied from a
    chiller
    """

    pass


class Collection_Basin_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of the water in the collection basin, e.g.
    within a Cooling_Tower
    """

    pass


class Condenser_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of condenser water
    """

    pass


class Entering_Condenser_Water_Temperature_Sensor(Condenser_Water_Temperature_Sensor):
    """
    Measures the temperature of the entering condenser water
    """

    pass


class Leaving_Condenser_Water_Temperature_Sensor(Condenser_Water_Temperature_Sensor):
    """
    Measures the temperature of the leaving condenser water
    """

    pass


class Return_Condenser_Water_Temperature_Sensor(Condenser_Water_Temperature_Sensor):
    pass


class Discharge_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Chilled_Water_Discharge_Temperature_Sensor(
    Discharge_Water_Temperature_Sensor, Chilled_Water_Temperature_Sensor
):
    pass


class Discharge_Condenser_Water_Temperature_Sensor(
    Discharge_Water_Temperature_Sensor, Condenser_Water_Temperature_Sensor
):
    pass


class Discharge_Condenser_Water_Temperature_Setpoint(
    Discharge_Water_Temperature_Sensor
):
    pass


class Discharge_Hot_Water_Temperature_Setpoint(Discharge_Water_Temperature_Sensor):
    pass


class Domestic_Hot_Water_Discharge_Temperature_Setpoint(
    Discharge_Hot_Water_Temperature_Setpoint
):
    pass


class Hot_Water_Discharge_Temperature_Sensor(Discharge_Water_Temperature_Sensor):
    pass


class High_Temperature_Hot_Water_Discharge_Temperature_Sensor(
    Hot_Water_Discharge_Temperature_Sensor
):
    pass


class Medium_Temperature_Hot_Water_Discharge_Temperature_Sensor(
    Hot_Water_Discharge_Temperature_Sensor
):
    pass


class Domestic_Hot_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Domestic_Hot_Water_Discharge_Temperature_Sensor(
    Domestic_Hot_Water_Temperature_Sensor
):
    pass


class Entering_Hot_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of water enteringed to a hot water system
    """

    pass


class Entering_Domestic_Hot_Water_Temperature_Sensor(
    Entering_Hot_Water_Temperature_Sensor, Domestic_Hot_Water_Temperature_Sensor
):
    pass


class Entering_High_Temperature_Hot_Water_Temperature_Sensor(
    Entering_Hot_Water_Temperature_Sensor
):
    """
    Measures the temperature of high-temperature hot water enteringed to a
    hot water system
    """

    pass


class Entering_Medium_Temperature_Hot_Water_Temperature_Sensor(
    Entering_Hot_Water_Temperature_Sensor
):
    """
    Measures the temperature of medium-temperature hot water entering a
    hot water system
    """

    pass


class Entering_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of entering water
    """

    pass


class Heat_Exchanger_Discharge_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Heat_Exchanger_Supply_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Leaving_Hot_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of water supplied by a hot water system
    """

    pass


class Leaving_Domestic_Hot_Water_Temperature_Sensor(
    Leaving_Hot_Water_Temperature_Sensor, Domestic_Hot_Water_Temperature_Sensor
):
    """
    Measures the temperature of domestic water supplied by a hot water
    system
    """

    pass


class Leaving_High_Temperature_Hot_Water_Temperature_Sensor(
    Leaving_Hot_Water_Temperature_Sensor
):
    """
    Measures the temperature of high-temperature hot water supplied by a
    hot water system
    """

    pass


class Leaving_Medium_Temperature_Hot_Water_Temperature_Sensor(
    Leaving_Hot_Water_Temperature_Sensor
):
    """
    Measures the temperature of medium-temperature hot water supplied by a
    hot water system
    """

    pass


class Leaving_Water_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the temperature of water leaving a piece of equipment or
    system
    """

    pass


class Heat_Exchanger_Leaving_Water_Temperature_Sensor(Leaving_Water_Temperature_Sensor):
    pass


class Ice_Tank_Leaving_Water_Temperature_Sensor(Leaving_Water_Temperature_Sensor):
    """
    Measures the temperature of water leaving an ice tank
    """

    pass


class Return_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Chilled_Water_Return_Temperature_Sensor(
    Return_Water_Temperature_Sensor, Chilled_Water_Temperature_Sensor
):
    pass


class Hot_Water_Return_Temperature_Sensor(Return_Water_Temperature_Sensor):
    pass


class High_Temperature_Hot_Water_Return_Temperature_Sensor(
    Hot_Water_Return_Temperature_Sensor
):
    pass


class Medium_Temperature_Hot_Water_Return_Temperature_Sensor(
    Hot_Water_Return_Temperature_Sensor
):
    pass


class Supply_Water_Temperature_Sensor(Water_Temperature_Sensor):
    pass


class Chilled_Water_Supply_Temperature_Sensor(
    Supply_Water_Temperature_Sensor, Chilled_Water_Temperature_Sensor
):
    pass


class Hot_Water_Supply_Flow_Setpoint(Supply_Water_Temperature_Sensor):
    pass


class Hot_Water_Supply_Temperature_Sensor(Supply_Water_Temperature_Sensor):
    pass


class Domestic_Hot_Water_Supply_Temperature_Sensor(Hot_Water_Supply_Temperature_Sensor):
    pass


class High_Temperature_Hot_Water_Supply_Temperature_Sensor(
    Hot_Water_Supply_Temperature_Sensor
):
    pass


class Medium_Temperature_Hot_Water_Supply_Temperature_Sensor(
    Hot_Water_Supply_Temperature_Sensor
):
    pass


class Supply_Condenser_Water_Temperature_Sensor(
    Supply_Water_Temperature_Sensor, Condenser_Water_Temperature_Sensor
):
    pass


class Supply_Condenser_Water_Temperature_Setpoint(Supply_Water_Temperature_Sensor):
    pass


class Supply_Hot_Water_Temperature_Setpoint(Supply_Water_Temperature_Sensor):
    pass


class Domestic_Hot_Water_Supply_Temperature_Setpoint(
    Supply_Hot_Water_Temperature_Setpoint
):
    pass


class Water_Differential_Temperature_Sensor(Water_Temperature_Sensor):
    """
    Measures the difference in water temperature between an upstream and
    downstream point in a pipe or conduit
    """

    pass


class Chilled_Water_Differential_Temperature_Sensor(
    Water_Differential_Temperature_Sensor, Chilled_Water_Temperature_Sensor
):
    """
    Measures the difference in temperature between the entering water to
    the chiller or other water cooling device and leaving water from the
    same chiller or other water cooling device
    """

    pass


class Differential_Discharge_Return_Water_Temperature_Sensor(
    Water_Differential_Temperature_Sensor
):
    pass


class Differential_Supply_Return_Water_Temperature_Sensor(
    Water_Differential_Temperature_Sensor
):
    pass


class Hot_Water_Differential_Temperature_Sensor(Water_Differential_Temperature_Sensor):
    """
    Measures the difference in temperature between the entering water to
    the boiler or other water heating device and leaving water from the
    same boiler or other water heating device
    """

    pass


class Torque_Sensor(Sensor):
    """
    Measures torque, the tendency of a force to rotate an object about
    some axis
    """

    pass


class Motor_Torque_Sensor(Torque_Sensor):
    """
    Measures the torque, or rotating power, of a motor
    """

    pass


class Usage_Sensor(Sensor):
    """
    Measures the amount of some substance that is consumed or used, over
    some period of time
    """

    pass


class Energy_Usage_Sensor(Usage_Sensor, Energy_Sensor):
    """
    Measures the total amount of energy used over some period of time
    """

    pass


class Electrical_Energy_Usage_Sensor(Energy_Usage_Sensor):
    """
    A sensor that records the quantity of electrical energy consumed in a
    given period
    """

    pass


class Thermal_Energy_Usage_Sensor(Energy_Usage_Sensor):
    """
    A sensor that records the quantity of thermal energy consumed in a
    given period
    """

    pass


class Natural_Gas_Usage_Sensor(Usage_Sensor):
    """
    Measures the amount of natural gas that is consumed or used, over some
    period of time
    """

    pass


class Steam_Usage_Sensor(Usage_Sensor):
    """
    Measures the amount of steam that is consumed or used, over some
    period of time
    """

    pass


class Water_Usage_Sensor(Usage_Sensor):
    """
    Measures the amount of water that is consumed, over some period of
    time
    """

    pass


class Hot_Water_Usage_Sensor(Water_Usage_Sensor):
    """
    Measures the amount of hot water that is consumed, over some period of
    time
    """

    pass


class Voltage_Sensor(Sensor):
    """
    Measures the voltage of an electrical device or object
    """

    pass


class Battery_Voltage_Sensor(Voltage_Sensor):
    """
    Measures the capacity of a battery
    """

    pass


class DC_Bus_Voltage_Sensor(Voltage_Sensor):
    """
    Measures the voltage across a DC bus
    """

    pass


class Output_Voltage_Sensor(Voltage_Sensor):
    """
    Measures the voltage output by some process or device
    """

    pass


class Waste_Amount_Sensor(Sensor):
    """
    A metric used for measuring the quantity of waste generated in a
    building.
    """

    pass


class Water_Level_Sensor(Sensor):
    """
    Measures the height/level of water in some container
    """

    pass


class Collection_Basin_Water_Level_Sensor(Water_Level_Sensor):
    """
    Measures the level of the water in the collection basin, e.g. within a
    Cooling_Tower
    """

    pass


class Deionised_Water_Level_Sensor(Water_Level_Sensor):
    """
    Measures the height/level of deionised water in some container
    """

    pass


class Setpoint(Point):
    """
    A Setpoint is an input value at which the desired property is set
    """

    pass


class CO2_Setpoint(Setpoint):
    """
    Sets some property of CO2
    """

    pass


class Return_Air_CO2_Setpoint(CO2_Setpoint):
    """
    Sets some property of CO2 in Return Air
    """

    pass


class Current_Ratio_Setpoint(Setpoint):
    """
    Sets the ratio of currents in a transformer
    """

    pass


class Damper_Position_Setpoint(Setpoint):
    """
    Sets the position of damper
    """

    pass


class Deadband_Setpoint(Setpoint):
    """
    Sets the size of a deadband
    """

    pass


class Humidity_Deadband_Setpoint(Deadband_Setpoint):
    """
    Sets the size of a deadband of humidity
    """

    pass


class Demand_Setpoint(Setpoint):
    """
    Sets the rate required for a process
    """

    pass


class Cooling_Demand_Setpoint(Demand_Setpoint):
    """
    Sets the rate required for cooling
    """

    pass


class Heating_Demand_Setpoint(Demand_Setpoint):
    """
    Sets the rate required for heating
    """

    pass


class Preheat_Demand_Setpoint(Demand_Setpoint):
    """
    Sets the rate required for preheat
    """

    pass


class Dewpoint_Setpoint(Setpoint):
    """
    Sets dew point
    """

    pass


class Differential_Setpoint(Setpoint):
    """
    A type of Setpoints that is related to the difference between two
    measurements
    """

    pass


class Differential_Pressure_Deadband_Setpoint(Differential_Setpoint):
    """
    Sets the size of a deadband of differential pressure
    """

    pass


class Chilled_Water_Differential_Pressure_Deadband_Setpoint(
    Differential_Pressure_Deadband_Setpoint
):
    """
    Sets the size of a deadband of differential pressure of chilled water
    """

    pass


class Entering_Water_Differential_Pressure_Deadband_Setpoint(
    Differential_Pressure_Deadband_Setpoint
):
    """
    Sets the size of a deadband of differential pressure of entering water
    """

    pass


class Hot_Water_Differential_Pressure_Deadband_Setpoint(
    Differential_Pressure_Deadband_Setpoint
):
    """
    Sets the size of a deadband of differential pressure of hot water
    """

    pass


class Leaving_Water_Differential_Pressure_Deadband_Setpoint(
    Differential_Pressure_Deadband_Setpoint
):
    """
    Sets the size of a deadband of differential pressure of leaving water
    """

    pass


class Differential_Pressure_Setpoint(Differential_Setpoint):
    """
    Sets differential pressure
    """

    pass


class Air_Differential_Pressure_Setpoint(Differential_Pressure_Setpoint):
    """
    Sets the target air differential pressure between an upstream and
    downstream point in a air duct or conduit
    """

    pass


class Discharge_Air_Differential_Pressure_Setpoint(Air_Differential_Pressure_Setpoint):
    pass


class Exhaust_Air_Differential_Pressure_Setpoint(Air_Differential_Pressure_Setpoint):
    """
    Sets the target air differential pressure between an upstream and
    downstream point in a exhaust air duct or conduit
    """

    pass


class Return_Air_Differential_Pressure_Setpoint(Air_Differential_Pressure_Setpoint):
    """
    Sets the target air differential pressure between an upstream and
    downstream point in a return air duct or conduit
    """

    pass


class Supply_Air_Differential_Pressure_Setpoint(Air_Differential_Pressure_Setpoint):
    """
    Sets the target air differential pressure between an upstream and
    downstream point in a supply air duct or conduit
    """

    pass


class Water_Differential_Pressure_Setpoint(Differential_Pressure_Setpoint):
    """
    Sets the target water differential pressure between an upstream and
    downstream point in a water pipe or conduit
    """

    pass


class Chilled_Water_Differential_Pressure_Setpoint(
    Water_Differential_Pressure_Setpoint
):
    """
    Sets the target water differential pressure between an upstream and
    downstream point in a water pipe or conduit used to carry chilled
    water
    """

    pass


class Hot_Water_Differential_Pressure_Setpoint(Water_Differential_Pressure_Setpoint):
    """
    Sets the target water differential pressure between an upstream and
    downstream point in a water pipe or conduit used to carry hot water
    """

    pass


class Domestic_Hot_Water_Differential_Pressure_Setpoint(
    Hot_Water_Differential_Pressure_Setpoint
):
    """
    Sets the target water differential pressure between an upstream and
    downstream point in a water pipe used to carry domestic hot water
    """

    pass


class Medium_Temperature_Hot_Water_Differential_Pressure_Setpoint(
    Hot_Water_Differential_Pressure_Setpoint
):
    pass


class Differential_Speed_Setpoint(Differential_Setpoint):
    """
    Sets differential speed
    """

    pass


class Differential_Temperature_Setpoint(Differential_Setpoint):
    """
    A type of Setpoints that is related to the difference between two
    temperature measurements
    """

    pass


class Differential_Air_Temperature_Setpoint(Differential_Temperature_Setpoint):
    """
    Sets temperature of diffrential air
    """

    pass


class Water_Differential_Temperature_Setpoint(Differential_Temperature_Setpoint):
    """
    Sets the target differential temperature between the start and end of
    a heat transfer cycle in a water circuit
    """

    pass


class Medium_Temperature_Hot_Water_Differential_Pressure_Load_Shed_Setpoint(
    Differential_Setpoint
):
    pass


class Temperature_Differential_Reset_Setpoint(Differential_Setpoint):
    pass


class Discharge_Air_Temperature_Reset_Differential_Setpoint(
    Temperature_Differential_Reset_Setpoint
):
    pass


class Supply_Air_Temperature_Reset_Differential_Setpoint(
    Temperature_Differential_Reset_Setpoint
):
    pass


class Enthalpy_Setpoint(Setpoint):
    """
    Sets enthalpy
    """

    pass


class Flow_Setpoint(Setpoint):
    """
    Sets flow
    """

    pass


class Air_Flow_Setpoint(Flow_Setpoint):
    """
    Sets air flow
    """

    pass


class Air_Flow_Deadband_Setpoint(Air_Flow_Setpoint, Deadband_Setpoint):
    """
    Sets the size of a deadband of air flow
    """

    pass


class Air_Flow_Demand_Setpoint(Demand_Setpoint, Air_Flow_Setpoint):
    """
    Sets the rate of air flow required for a process
    """

    pass


class Discharge_Air_Flow_Setpoint(Air_Flow_Setpoint):
    """
    Sets discharge air flow
    """

    pass


class Exhaust_Air_Flow_Setpoint(Air_Flow_Setpoint):
    """
    Sets exhaust air flow rate
    """

    pass


class Exhaust_Air_Stack_Flow_Setpoint(Exhaust_Air_Flow_Setpoint):
    """
    Sets exhaust air stack flow rate
    """

    pass


class Exhaust_Air_Stack_Flow_Deadband_Setpoint(
    Exhaust_Air_Stack_Flow_Setpoint, Air_Flow_Deadband_Setpoint
):
    """
    Sets the size of a deadband of exhaust air stack flow
    """

    pass


class Outside_Air_Flow_Setpoint(Air_Flow_Setpoint):
    """
    Sets outside air flow rate
    """

    pass


class Supply_Air_Flow_Setpoint(Air_Flow_Setpoint):
    """
    Sets supply air flow rate
    """

    pass


class Cooling_Discharge_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets discharge air flow for cooling
    """

    pass


class Cooling_Supply_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets supply air flow rate for cooling
    """

    pass


class Discharge_Air_Flow_Demand_Setpoint(
    Air_Flow_Demand_Setpoint, Supply_Air_Flow_Setpoint
):
    """
    Sets the rate of discharge air flow required for a process
    """

    pass


class Heating_Discharge_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets discharge air flow for heating
    """

    pass


class Heating_Supply_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets supply air flow rate for heating
    """

    pass


class Occupied_Discharge_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets discharge air flow when occupied
    """

    pass


class Occupied_Supply_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    """
    Sets supply air flow rate when occupied
    """

    pass


class Occupied_Cooling_Discharge_Air_Flow_Setpoint(
    Occupied_Supply_Air_Flow_Setpoint,
    Cooling_Supply_Air_Flow_Setpoint,
    Cooling_Discharge_Air_Flow_Setpoint,
):
    """
    Sets discharge air flow for cooling when occupied
    """

    pass


class Occupied_Cooling_Supply_Air_Flow_Setpoint(
    Occupied_Supply_Air_Flow_Setpoint,
    Cooling_Supply_Air_Flow_Setpoint,
    Cooling_Discharge_Air_Flow_Setpoint,
):
    """
    Sets supply air flow rate for cooling when occupied
    """

    pass


class Occupied_Heating_Discharge_Air_Flow_Setpoint(
    Occupied_Supply_Air_Flow_Setpoint,
    Heating_Supply_Air_Flow_Setpoint,
    Heating_Discharge_Air_Flow_Setpoint,
):
    """
    Sets discharge air flow for heating when occupied
    """

    pass


class Occupied_Heating_Supply_Air_Flow_Setpoint(
    Occupied_Supply_Air_Flow_Setpoint,
    Heating_Supply_Air_Flow_Setpoint,
    Heating_Discharge_Air_Flow_Setpoint,
):
    """
    Sets supply air flow rate for heating when occupied
    """

    pass


class Supply_Air_Flow_Demand_Setpoint(
    Air_Flow_Demand_Setpoint, Supply_Air_Flow_Setpoint
):
    """
    Sets the rate of supply air flow required for a process
    """

    pass


class Unoccupied_Discharge_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    pass


class Unoccupied_Supply_Air_Flow_Setpoint(Supply_Air_Flow_Setpoint):
    pass


class Unoccupied_Cooling_Discharge_Air_Flow_Setpoint(
    Unoccupied_Supply_Air_Flow_Setpoint,
    Cooling_Supply_Air_Flow_Setpoint,
    Cooling_Discharge_Air_Flow_Setpoint,
):
    """
    Sets discharge air flow for cooling when unoccupied
    """

    pass


class Unoccupied_Cooling_Supply_Air_Flow_Setpoint(
    Unoccupied_Supply_Air_Flow_Setpoint,
    Cooling_Supply_Air_Flow_Setpoint,
    Cooling_Discharge_Air_Flow_Setpoint,
):
    pass


class Unoccupied_Heating_Discharge_Air_Flow_Setpoint(
    Unoccupied_Supply_Air_Flow_Setpoint,
    Heating_Supply_Air_Flow_Setpoint,
    Heating_Discharge_Air_Flow_Setpoint,
):
    pass


class Unoccupied_Heating_Supply_Air_Flow_Setpoint(
    Unoccupied_Supply_Air_Flow_Setpoint,
    Heating_Supply_Air_Flow_Setpoint,
    Heating_Discharge_Air_Flow_Setpoint,
):
    pass


class Water_Flow_Setpoint(Flow_Setpoint):
    """
    Sets the target flow rate of water
    """

    pass


class Bypass_Water_Flow_Setpoint(Water_Flow_Setpoint):
    """
    Sets the target flow rate of bypass water
    """

    pass


class Chilled_Water_Flow_Setpoint(Water_Flow_Setpoint):
    """
    Sets the target flow rate of chilled water
    """

    pass


class Condenser_Water_Flow_Setpoint(Water_Flow_Setpoint):
    pass


class Discharge_Water_Flow_Setpoint(Water_Flow_Setpoint):
    pass


class Chilled_Water_Discharge_Flow_Setpoint(
    Chilled_Water_Flow_Setpoint, Discharge_Water_Flow_Setpoint
):
    pass


class Entering_Water_Flow_Setpoint(Water_Flow_Setpoint):
    """
    Sets the target flow rate of entering water
    """

    pass


class Entering_Chilled_Water_Flow_Setpoint(
    Chilled_Water_Flow_Setpoint, Entering_Water_Flow_Setpoint
):
    """
    Sets the target flow rate of chilled entering water
    """

    pass


class Hot_Water_Flow_Setpoint(Water_Flow_Setpoint):
    """
    Sets the target flow rate of hot water
    """

    pass


class Entering_Hot_Water_Flow_Setpoint(
    Hot_Water_Flow_Setpoint, Entering_Water_Flow_Setpoint
):
    """
    Sets the target flow rate of hot entering water
    """

    pass


class Hot_Water_Discharge_Flow_Setpoint(
    Hot_Water_Flow_Setpoint, Discharge_Water_Flow_Setpoint
):
    pass


class Leaving_Water_Flow_Setpoint(Water_Flow_Setpoint):
    """
    Sets the target flow rate of leaving water
    """

    pass


class Leaving_Chilled_Water_Flow_Setpoint(
    Leaving_Water_Flow_Setpoint, Chilled_Water_Flow_Setpoint
):
    """
    Sets the target flow rate of chilled leaving water
    """

    pass


class Leaving_Hot_Water_Flow_Setpoint(
    Leaving_Water_Flow_Setpoint, Hot_Water_Flow_Setpoint
):
    """
    Sets the target flow rate of hot leaving water
    """

    pass


class Supply_Water_Flow_Setpoint(Water_Flow_Setpoint):
    pass


class Chilled_Water_Supply_Flow_Setpoint(
    Chilled_Water_Flow_Setpoint, Supply_Water_Flow_Setpoint
):
    pass


class Frequency_Setpoint(Setpoint):
    """
    Sets frequency
    """

    pass


class Humidity_Setpoint(Setpoint):
    """
    Sets humidity
    """

    pass


class Building_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Setpoint for humidity in a building
    """

    pass


class Bypass_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for bypass air
    """

    pass


class Discharge_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for discharge air
    """

    pass


class Exhaust_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for exhaust air
    """

    pass


class Mixed_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for mixed air
    """

    pass


class Occupied_Humidity_Setpoint(Humidity_Setpoint):
    """
    Target humidity level when the location is occupied.
    """

    pass


class Outside_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for outside air
    """

    pass


class Return_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for return air
    """

    pass


class Supply_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for supply air
    """

    pass


class Unoccupied_Humidity_Setpoint(Humidity_Setpoint):
    """
    Target humidity level when the location is unoccupied.
    """

    pass


class Zone_Air_Humidity_Setpoint(Humidity_Setpoint):
    """
    Humidity setpoint for zone air
    """

    pass


class Illuminance_Setpoint(Setpoint):
    """
    Target Illuminance of the zone.
    """

    pass


class Load_Setpoint(Setpoint):
    pass


class Load_Shed_Setpoint(Load_Setpoint):
    pass


class Entering_Medium_Temperature_Hot_Water_Temperature_Load_Shed_Setpoint(
    Load_Shed_Setpoint
):
    pass


class Leaving_Medium_Temperature_Hot_Water_Temperature_Load_Shed_Setpoint(
    Load_Shed_Setpoint
):
    pass


class Load_Shed_Differential_Pressure_Setpoint(
    Load_Shed_Setpoint, Differential_Pressure_Setpoint
):
    pass


class Chilled_Water_Differential_Pressure_Load_Shed_Setpoint(
    Load_Shed_Differential_Pressure_Setpoint,
    Chilled_Water_Differential_Pressure_Setpoint,
):
    pass


class Luminance_Setpoint(Setpoint):
    """
    Sets luminance
    """

    pass


class Pressure_Setpoint(Setpoint):
    """
    Sets pressure
    """

    pass


class Air_Pressure_Setpoint(Pressure_Setpoint):
    pass


class Static_Pressure_Setpoint(Pressure_Setpoint):
    """
    Sets static pressure
    """

    pass


class Building_Air_Static_Pressure_Setpoint(
    Static_Pressure_Setpoint, Air_Pressure_Setpoint
):
    """
    Sets static pressure of the entire building
    """

    pass


class Chilled_Water_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets static pressure of chilled water
    """

    pass


class Discharge_Air_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets static pressure of discharge air
    """

    pass


class Duct_Air_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    pass


class Exhaust_Air_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets static pressure of exhaust air
    """

    pass


class Hot_Water_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets static pressure of hot air
    """

    pass


class Static_Pressure_Deadband_Setpoint(Static_Pressure_Setpoint, Deadband_Setpoint):
    """
    Sets the size of a deadband of static pressure
    """

    pass


class Supply_Air_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets static pressure of supply air
    """

    pass


class Discharge_Air_Static_Pressure_Deadband_Setpoint(
    Supply_Air_Static_Pressure_Setpoint,
    Discharge_Air_Static_Pressure_Setpoint,
    Static_Pressure_Deadband_Setpoint,
):
    """
    Sets the size of a deadband of static pressure of discharge air
    """

    pass


class Supply_Air_Static_Pressure_Deadband_Setpoint(
    Supply_Air_Static_Pressure_Setpoint,
    Discharge_Air_Static_Pressure_Setpoint,
    Static_Pressure_Deadband_Setpoint,
):
    """
    Sets the size of a deadband of static pressure of supply air
    """

    pass


class Underfloor_Air_Plenum_Static_Pressure_Setpoint(Static_Pressure_Setpoint):
    """
    Sets the underfloor air plenum static pressure
    """

    pass


class Velocity_Pressure_Setpoint(Pressure_Setpoint):
    """
    Sets static veloicty pressure
    """

    pass


class Water_Pressure_Setpoint(Pressure_Setpoint):
    pass


class Reset_Setpoint(Setpoint):
    """
    Setpoints used in reset strategies
    """

    pass


class Discharge_Air_Flow_Reset_Setpoint(Reset_Setpoint):
    """
    Setpoints used in Reset strategies
    """

    pass


class Supply_Air_Flow_Reset_Setpoint(Reset_Setpoint):
    pass


class Discharge_Air_Flow_High_Reset_Setpoint(Supply_Air_Flow_Reset_Setpoint):
    pass


class Discharge_Air_Flow_Low_Reset_Setpoint(Supply_Air_Flow_Reset_Setpoint):
    pass


class Supply_Air_Flow_High_Reset_Setpoint(Supply_Air_Flow_Reset_Setpoint):
    pass


class Supply_Air_Flow_Low_Reset_Setpoint(Supply_Air_Flow_Reset_Setpoint):
    pass


class Temperature_High_Reset_Setpoint(Reset_Setpoint):
    pass


class Discharge_Air_Temperature_High_Reset_Setpoint(
    Supply_Air_Temperature_Reset_Differential_Setpoint, Temperature_High_Reset_Setpoint
):
    pass


class Entering_Hot_Water_Temperature_High_Reset_Setpoint(
    Temperature_High_Reset_Setpoint
):
    pass


class Entering_Medium_Temperature_Hot_Water_Temperature_High_Reset_Setpoint(
    Entering_Hot_Water_Temperature_High_Reset_Setpoint
):
    pass


class Leaving_Hot_Water_Temperature_High_Reset_Setpoint(
    Temperature_High_Reset_Setpoint
):
    pass


class Leaving_Medium_Temperature_Hot_Water_Temperature_High_Reset_Setpoint(
    Leaving_Hot_Water_Temperature_High_Reset_Setpoint
):
    pass


class Outside_Air_Temperature_High_Reset_Setpoint(Temperature_High_Reset_Setpoint):
    pass


class Return_Air_Temperature_High_Reset_Setpoint(Temperature_High_Reset_Setpoint):
    pass


class Supply_Air_Temperature_High_Reset_Setpoint(
    Supply_Air_Temperature_Reset_Differential_Setpoint, Temperature_High_Reset_Setpoint
):
    pass


class Temperature_Low_Reset_Setpoint(Reset_Setpoint):
    pass


class Discharge_Air_Temperature_Low_Reset_Setpoint(
    Supply_Air_Temperature_Reset_Differential_Setpoint, Temperature_Low_Reset_Setpoint
):
    pass


class Entering_Hot_Water_Temperature_Low_Reset_Setpoint(Temperature_Low_Reset_Setpoint):
    pass


class Entering_Medium_Temperature_Hot_Water_Temperature_Low_Reset_Setpoint(
    Entering_Hot_Water_Temperature_Low_Reset_Setpoint
):
    pass


class Leaving_Hot_Water_Temperature_Low_Reset_Setpoint(Temperature_Low_Reset_Setpoint):
    pass


class Leaving_Medium_Temperature_Hot_Water_Temperature_Low_Reset_Setpoint(
    Leaving_Hot_Water_Temperature_Low_Reset_Setpoint
):
    pass


class Outside_Air_Temperature_Low_Reset_Setpoint(Temperature_Low_Reset_Setpoint):
    pass


class Return_Air_Temperature_Low_Reset_Setpoint(Temperature_Low_Reset_Setpoint):
    pass


class Supply_Air_Temperature_Low_Reset_Setpoint(
    Supply_Air_Temperature_Reset_Differential_Setpoint, Temperature_Low_Reset_Setpoint
):
    pass


class Speed_Setpoint(Setpoint):
    """
    Sets speed
    """

    pass


class Rated_Speed_Setpoint(Speed_Setpoint):
    """
    Sets rated speed
    """

    pass


class Temperature_Setpoint(Setpoint):
    """
    Sets temperature
    """

    pass


class Air_Temperature_Setpoint(Temperature_Setpoint):
    """
    Sets temperature of air
    """

    pass


class Cooling_Zone_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    The cooling setpoint for a specific zone in a building.
    """

    pass


class Standby_Cooling_Zone_Air_Temperature_Setpoint(
    Cooling_Zone_Air_Temperature_Setpoint
):
    pass


class Discharge_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of discharge air
    """

    pass


class Effective_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    pass


class Effective_Air_Temperature_Cooling_Setpoint(Effective_Air_Temperature_Setpoint):
    pass


class Effective_Air_Temperature_Heating_Setpoint(Effective_Air_Temperature_Setpoint):
    pass


class Effective_Cooling_Zone_Air_Temperature_Setpoint(
    Effective_Air_Temperature_Setpoint, Cooling_Zone_Air_Temperature_Setpoint
):
    """
    The effective cooling setpoint for a specific zone in a building.
    """

    pass


class Heating_Zone_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    The heating setpoint for a specific zone in a building.
    """

    pass


class Effective_Heating_Zone_Air_Temperature_Setpoint(
    Effective_Air_Temperature_Setpoint, Heating_Zone_Air_Temperature_Setpoint
):
    """
    The effective heating setpoint for a specific zone in a building.
    """

    pass


class Standby_Heating_Zone_Air_Temperature_Setpoint(
    Heating_Zone_Air_Temperature_Setpoint
):
    pass


class Max_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Setpoint for maximum air temperature
    """

    pass


class Min_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Setpoint for minimum air temperature
    """

    pass


class Mixed_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of mixed air
    """

    pass


class Occupied_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    pass


class Occupied_Air_Temperature_Cooling_Setpoint(Occupied_Air_Temperature_Setpoint):
    pass


class Occupied_Air_Temperature_Heating_Setpoint(Occupied_Air_Temperature_Setpoint):
    pass


class Occupied_Cooling_Zone_Air_Temperature_Setpoint(
    Occupied_Air_Temperature_Setpoint, Cooling_Zone_Air_Temperature_Setpoint
):
    """
    Sets temperature for zone air cooling when occupied
    """

    pass


class Occupied_Heating_Zone_Air_Temperature_Setpoint(
    Occupied_Air_Temperature_Setpoint, Heating_Zone_Air_Temperature_Setpoint
):
    """
    Sets temperature for zone air heating when occupied
    """

    pass


class Outside_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of outside air
    """

    pass


class Disable_Hot_Water_System_Outside_Air_Temperature_Setpoint(
    Outside_Air_Temperature_Setpoint
):
    """
    Disables hot water system when outside air temperature reaches the
    indicated value
    """

    pass


class Enable_Hot_Water_System_Outside_Air_Temperature_Setpoint(
    Outside_Air_Temperature_Setpoint
):
    """
    Enables hot water system when outside air temperature reaches the
    indicated value
    """

    pass


class Low_Outside_Air_Temperature_Enable_Setpoint(Outside_Air_Temperature_Setpoint):
    pass


class Outside_Air_Lockout_Temperature_Setpoint(Outside_Air_Temperature_Setpoint):
    pass


class Return_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    The target temperature for return air, often used as an approximation
    of zone air temperature
    """

    pass


class Effective_Return_Air_Temperature_Setpoint(
    Return_Air_Temperature_Setpoint, Effective_Air_Temperature_Setpoint
):
    pass


class Occupied_Return_Air_Temperature_Setpoint(
    Return_Air_Temperature_Setpoint, Occupied_Air_Temperature_Setpoint
):
    pass


class Room_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of room air
    """

    pass


class Effective_Room_Air_Temperature_Setpoint(
    Room_Air_Temperature_Setpoint, Effective_Air_Temperature_Setpoint
):
    pass


class Occupied_Room_Air_Temperature_Setpoint(
    Room_Air_Temperature_Setpoint, Occupied_Air_Temperature_Setpoint
):
    pass


class Supply_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Temperature setpoint for supply air
    """

    pass


class Effective_Discharge_Air_Temperature_Setpoint(
    Effective_Air_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    pass


class Effective_Supply_Air_Temperature_Setpoint(
    Effective_Air_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    pass


class Occupied_Discharge_Air_Temperature_Setpoint(
    Supply_Air_Temperature_Setpoint, Occupied_Air_Temperature_Setpoint
):
    pass


class Occupied_Supply_Air_Temperature_Setpoint(
    Supply_Air_Temperature_Setpoint, Occupied_Air_Temperature_Setpoint
):
    pass


class Target_Zone_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    pass


class Effective_Target_Zone_Air_Temperature_Setpoint(
    Effective_Air_Temperature_Setpoint, Target_Zone_Air_Temperature_Setpoint
):
    """
    Target Setpoint (also known as Common Setpoint) is a reference point
    representing the desired air temperature in a specific zone of a
    building. This setpoint acts as a baseline from which the cooling and
    heating setpoints are established by adding or subtracting a deadband
    width
    """

    pass


class Occupied_Target_Zone_Air_Temperature_Setpoint(
    Occupied_Air_Temperature_Setpoint, Target_Zone_Air_Temperature_Setpoint
):
    """
    Target Setpoint (also known as Common Setpoint) is a reference point
    representing the desired occupied air temperature in a specific zone
    of a building. This setpoint acts as a baseline from which deadband
    setpoints are established by adding or subtracting a deadband width.
    """

    pass


class Standby_Target_Zone_Air_Temperature_Setpoint(
    Target_Zone_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of air when unoccupied
    """

    pass


class Unoccupied_Air_Temperature_Cooling_Setpoint(Unoccupied_Air_Temperature_Setpoint):
    pass


class Unoccupied_Air_Temperature_Heating_Setpoint(Unoccupied_Air_Temperature_Setpoint):
    pass


class Unoccupied_Cooling_Zone_Air_Temperature_Setpoint(
    Unoccupied_Air_Temperature_Setpoint, Cooling_Zone_Air_Temperature_Setpoint
):
    """
    Sets temperature of air when unoccupied for cooling within a specific
    zone
    """

    pass


class Unoccupied_Discharge_Air_Temperature_Setpoint(
    Supply_Air_Temperature_Setpoint, Unoccupied_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Heating_Zone_Air_Temperature_Setpoint(
    Unoccupied_Air_Temperature_Setpoint, Heating_Zone_Air_Temperature_Setpoint
):
    """
    Sets temperature of air when unoccupied for heating within a specific
    zone
    """

    pass


class Unoccupied_Return_Air_Temperature_Setpoint(
    Return_Air_Temperature_Setpoint, Unoccupied_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Room_Air_Temperature_Setpoint(
    Room_Air_Temperature_Setpoint, Unoccupied_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Supply_Air_Temperature_Setpoint(
    Supply_Air_Temperature_Setpoint, Unoccupied_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Target_Zone_Air_Temperature_Setpoint(
    Unoccupied_Air_Temperature_Setpoint, Target_Zone_Air_Temperature_Setpoint
):
    """
    Target Setpoint (also known as Common Setpoint) is a reference point
    representing the desired unoccupied air temperature in a specific zone
    of a building. This setpoint acts as a baseline from which deadband
    setpoints are established by adding or subtracting a deadband width.
    """

    pass


class Zone_Air_Temperature_Setpoint(Air_Temperature_Setpoint):
    """
    Sets temperature of zone air
    """

    pass


class Effective_Zone_Air_Temperature_Setpoint(Zone_Air_Temperature_Setpoint):
    pass


class Occupied_Zone_Air_Temperaure_Setpoint(Zone_Air_Temperature_Setpoint):
    pass


class Unoccupied_Zone_Air_Temperature_Setpoint(Zone_Air_Temperature_Setpoint):
    pass


class Zone_Air_Cooling_Temperature_Setpoint(Zone_Air_Temperature_Setpoint):
    """
    The upper (cooling) setpoint for zone air temperature
    """

    pass


class Zone_Air_Heating_Temperature_Setpoint(Zone_Air_Temperature_Setpoint):
    """
    The lower (heating) setpoint for zone air temperature
    """

    pass


class Cooling_Temperature_Setpoint(Temperature_Setpoint):
    """
    Sets temperature for cooling
    """

    pass


class Discharge_Air_Temperature_Cooling_Setpoint(
    Cooling_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    """
    Sets temperature of discharge air for cooling
    """

    pass


class Occupied_Cooling_Temperature_Setpoint(Cooling_Temperature_Setpoint):
    """
    Sets temperature for cooling when occupied
    """

    pass


class Supply_Air_Temperature_Cooling_Setpoint(
    Cooling_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Cooling_Temperature_Setpoint(Cooling_Temperature_Setpoint):
    pass


class Heating_Temperature_Setpoint(Temperature_Setpoint):
    """
    Sets temperature for heating
    """

    pass


class Discharge_Air_Temperature_Heating_Setpoint(
    Heating_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    """
    Sets temperature of discharge air for heating
    """

    pass


class Occupied_Heating_Temperature_Setpoint(Heating_Temperature_Setpoint):
    """
    Sets temperature for heating when occupied
    """

    pass


class Open_Heating_Valve_Outside_Air_Temperature_Setpoint(
    Outside_Air_Temperature_Setpoint, Heating_Temperature_Setpoint
):
    pass


class Supply_Air_Temperature_Heating_Setpoint(
    Heating_Temperature_Setpoint, Supply_Air_Temperature_Setpoint
):
    pass


class Unoccupied_Heating_Temperature_Setpoint(Heating_Temperature_Setpoint):
    pass


class Radiant_Panel_Temperature_Setpoint(Temperature_Setpoint):
    """
    Sets temperature of radiant panel.
    """

    pass


class Embedded_Temperature_Setpoint(Radiant_Panel_Temperature_Setpoint):
    """
    Sets temperature for the internal material, e.g. concrete slab, of the
    radiant panel.
    """

    pass


class Core_Temperature_Setpoint(Embedded_Temperature_Setpoint):
    """
    Sets temperature for the core, i.e. the temperature at the heat source
    or sink level, of the radiant panel.
    """

    pass


class Inside_Face_Surface_Temperature_Setpoint(Radiant_Panel_Temperature_Setpoint):
    """
    Sets temperature for the inside face surface temperature of the
    radiant panel.
    """

    pass


class Outside_Face_Surface_Temperature_Setpoint(Radiant_Panel_Temperature_Setpoint):
    """
    Sets temperature for the outside face surface temperature of the
    radiant panel.
    """

    pass


class Schedule_Temperature_Setpoint(Temperature_Setpoint):
    """
    The current setpoint as indicated by the schedule
    """

    pass


class Temperature_Deadband_Setpoint(Temperature_Setpoint, Deadband_Setpoint):
    """
    Sets the size of a deadband of temperature
    """

    pass


class Discharge_Air_Temperature_Deadband_Setpoint(
    Discharge_Air_Temperature_Setpoint,
    Air_Temperature_Setpoint,
    Temperature_Deadband_Setpoint,
):
    """
    Sets the size of a deadband of temperature of discharge air
    """

    pass


class Occupied_Cooling_Temperature_Deadband_Setpoint(
    Cooling_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    """
    Sets the size of a deadband of temperature for cooling when occupied
    """

    pass


class Occupied_Heating_Temperature_Deadband_Setpoint(
    Heating_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    """
    Sets the size of a deadband of temperature for heating when occupied
    """

    pass


class Supply_Air_Temperature_Deadband_Setpoint(
    Discharge_Air_Temperature_Setpoint,
    Air_Temperature_Setpoint,
    Temperature_Deadband_Setpoint,
):
    """
    Sets the size of a deadband of temperature of supply air
    """

    pass


class Cooling_Discharge_Air_Temperature_Deadband_Setpoint(
    Supply_Air_Temperature_Deadband_Setpoint,
    Discharge_Air_Temperature_Cooling_Setpoint,
    Cooling_Temperature_Setpoint,
):
    """
    Sets the size of a deadband of temperature of cooling discharge air
    """

    pass


class Cooling_Supply_Air_Temperature_Deadband_Setpoint(
    Supply_Air_Temperature_Deadband_Setpoint,
    Discharge_Air_Temperature_Cooling_Setpoint,
    Cooling_Temperature_Setpoint,
):
    """
    Sets the size of a deadband of temperature of supply air for cooling
    """

    pass


class Heating_Discharge_Air_Temperature_Deadband_Setpoint(
    Supply_Air_Temperature_Deadband_Setpoint,
    Discharge_Air_Temperature_Heating_Setpoint,
    Heating_Temperature_Setpoint,
):
    """
    Sets the size of a deadband of temperature of heating discharge air
    """

    pass


class Heating_Supply_Air_Temperature_Deadband_Setpoint(
    Supply_Air_Temperature_Deadband_Setpoint,
    Discharge_Air_Temperature_Heating_Setpoint,
    Heating_Temperature_Setpoint,
):
    """
    Sets the size of a deadband of temperature of supply air for heating
    """

    pass


class Unoccupied_Cooling_Temperature_Deadband_Setpoint(
    Cooling_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    pass


class Unoccupied_Heating_Temperature_Deadband_Setpoint(
    Heating_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    pass


class Water_Temperature_Setpoint(Temperature_Setpoint):
    """
    Sets temperature of water
    """

    pass


class Chilled_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Sets the temperature of chilled water
    """

    pass


class Discharge_Chilled_Water_Temperature_Setpoint(Chilled_Water_Temperature_Setpoint):
    pass


class Supply_Chilled_Water_Temperature_Setpoint(Chilled_Water_Temperature_Setpoint):
    pass


class Entering_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Sets temperature of entering water
    """

    pass


class Entering_Chilled_Water_Temperature_Setpoint(
    Entering_Water_Temperature_Setpoint, Chilled_Water_Temperature_Setpoint
):
    """
    Sets the temperature of entering (downstream of the chilled water
    load) chilled water
    """

    pass


class Entering_Water_Temperature_Deadband_Setpoint(
    Entering_Water_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    """
    Sets the size of a deadband of temperature of entering water
    """

    pass


class Hot_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Sets the temperature of hot water
    """

    pass


class Domestic_Hot_Water_Temperature_Setpoint(
    Hot_Water_Temperature_Setpoint, Water_Temperature_Setpoint
):
    """
    Sets temperature of domestic hot water
    """

    pass


class Entering_Domestic_Hot_Water_Temperature_Setpoint(
    Entering_Water_Temperature_Setpoint, Domestic_Hot_Water_Temperature_Setpoint
):
    pass


class Entering_Hot_Water_Temperature_Setpoint(
    Entering_Water_Temperature_Setpoint, Hot_Water_Temperature_Setpoint
):
    """
    Sets the temperature of entering (downstream of the hot water load)
    hot water
    """

    pass


class Leaving_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Sets temperature of leaving water
    """

    pass


class Entering_Condenser_Water_Temperature_Setpoint(Leaving_Water_Temperature_Setpoint):
    """
    The temperature setpoint for the entering condenser water
    """

    pass


class Leaving_Chilled_Water_Temperature_Setpoint(
    Leaving_Water_Temperature_Setpoint, Chilled_Water_Temperature_Setpoint
):
    """
    Temperature setpoint for leaving chilled water
    """

    pass


class Leaving_Condenser_Water_Temperature_Setpoint(Leaving_Water_Temperature_Setpoint):
    """
    The temperature setpoint for the leaving condenser water
    """

    pass


class Leaving_Domestic_Hot_Water_Temperature_Setpoint(
    Leaving_Water_Temperature_Setpoint, Domestic_Hot_Water_Temperature_Setpoint
):
    """
    Sets temperature of leavinging part of domestic hot water
    """

    pass


class Leaving_Hot_Water_Temperature_Setpoint(
    Leaving_Water_Temperature_Setpoint, Hot_Water_Temperature_Setpoint
):
    """
    Temperature setpoint for leaving hot water
    """

    pass


class Leaving_Water_Temperature_Deadband_Setpoint(
    Leaving_Water_Temperature_Setpoint, Temperature_Deadband_Setpoint
):
    """
    Sets the size of a deadband of temperature of leaving water
    """

    pass


class Max_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Setpoint for max water temperature
    """

    pass


class Min_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    """
    Setpoint for min water temperature
    """

    pass


class Return_Water_Temperature_Setpoint(Water_Temperature_Setpoint):
    pass


class Return_Chilled_Water_Temperature_Setpoint(
    Chilled_Water_Temperature_Setpoint, Return_Water_Temperature_Setpoint
):
    pass


class Return_Condenser_Water_Temperature_Setpoint(Return_Water_Temperature_Setpoint):
    pass


class Return_Hot_Water_Temperature_Setpoint(Return_Water_Temperature_Setpoint):
    pass


class Time_Setpoint(Setpoint):
    pass


class Acceleration_Time_Setpoint(Time_Setpoint):
    pass


class Deceleration_Time_Setpoint(Time_Setpoint):
    pass


class Voltage_Ratio_Setpoint(Setpoint):
    """
    Sets the ratio of voltage in a transformer
    """

    pass


class Status(Point):
    """
    A Status is input point that reports the current operating mode,
    state, position, or condition of an item. Statuses are observations
    and should be considered 'read-only'
    """

    pass


class Availability_Status(Status):
    """
    Indicates if a piece of equipment, system, or functionality is
    available for operation
    """

    pass


class Damper_Position_Status(Status):
    pass


class Direction_Status(Status):
    """
    Indicates which direction a device is operating in
    """

    pass


class Motor_Direction_Status(Direction_Status):
    """
    Indicates which direction a motor is operating in, e.g. forward or
    reverse
    """

    pass


class Disable_Status(Status):
    """
    Indicates if functionality has been disabled
    """

    pass


class Drive_Ready_Status(Status):
    """
    Indicates if a hard drive or other storage device is ready to be used,
    e.g. in the context of RAID
    """

    pass


class Emergency_Generator_Status(Status):
    """
    Indicates if an emergency generator is active
    """

    pass


class Emergency_Push_Button_Status(Status):
    """
    Indicates if an emergency button has been pushed
    """

    pass


class Enable_Status(Status):
    """
    Indicates if a system or piece of functionality has been enabled
    """

    pass


class Even_Month_Status(Status):
    pass


class Fan_Status(Status):
    """
    Indicates properties of fans
    """

    pass


class Fault_Status(Status):
    """
    Indicates the presence of a fault in a device, system or control loop
    """

    pass


class Humidifier_Fault_Status(Fault_Status):
    """
    Indicates the presence of a fault in a humidifier
    """

    pass


class Last_Fault_Code_Status(Fault_Status):
    """
    Indicates the last fault code that occurred
    """

    pass


class Filter_Status(Status):
    """
    Indicates if a filter needs to be replaced
    """

    pass


class Pre_Filter_Status(Filter_Status):
    """
    Indicates if a prefilter needs to be replaced
    """

    pass


class Freeze_Status(Status):
    """
    Indicates if a substance contained within a vessel has frozen
    """

    pass


class Hold_Status(Status):
    pass


class Lead_Lag_Status(Status):
    """
    Indicates if lead/lag operation is enabled
    """

    pass


class Level_Status(Status):
    """
    The current operational state of a specific level within a predefined
    range.
    """

    pass


class Load_Shed_Status(Status):
    """
    Indicates if a load shedding policy is in effect
    """

    pass


class Entering_Hot_Water_Temperature_Load_Shed_Status(Load_Shed_Status):
    pass


class Entering_Medium_Temperature_Hot_Water_Temperature_Load_Shed_Status(
    Entering_Hot_Water_Temperature_Load_Shed_Status
):
    pass


class Leaving_Hot_Water_Temperature_Load_Shed_Status(Load_Shed_Status):
    pass


class Leaving_Medium_Temperature_Hot_Water_Temperature_Load_Shed_Status(
    Leaving_Hot_Water_Temperature_Load_Shed_Status
):
    pass


class Lockout_Status(Status):
    """
    Indicates if a piece of equipment, system, or functionality has been
    locked out from operation
    """

    pass


class Manual_Auto_Status(Status):
    """
    Indicates if a system is under manual or automatic operation
    """

    pass


class Mode_Status(Status):
    """
    Indicates which mode a system, device or control loop is currently in
    """

    pass


class Cooling_Mode_Status(Mode_Status):
    """
    Indicates whether a system, device or control loop is in a cooling
    mode
    """

    pass


class Heating_Mode_Status(Mode_Status):
    """
    Indicates whether a system, device or control loop is in a heating
    mode
    """

    pass


class Occupied_Mode_Status(Mode_Status):
    """
    Indicates if a system, device or control loop is in "Occupied" mode
    """

    pass


class Occupied_Cooling_Mode_Status(Occupied_Mode_Status, Cooling_Mode_Status):
    pass


class Occupied_Heating_Mode_Status(Heating_Mode_Status, Occupied_Mode_Status):
    pass


class Operating_Mode_Status(Mode_Status):
    """
    Indicates the current operating mode of a system, device or control
    loop
    """

    pass


class Vent_Operating_Mode_Status(Operating_Mode_Status):
    """
    Indicates the current operating mode of a vent
    """

    pass


class Speed_Mode_Status(Mode_Status):
    """
    Indicates the speed mode of a motor with various categorical settings,
    such as a multi-state value including low, medium, and high.
    """

    pass


class Unoccupied_Mode_Status(Mode_Status):
    pass


class Unoccupied_Cooling_Mode_Status(Unoccupied_Mode_Status, Cooling_Mode_Status):
    """
    Indicates whether a system, device or control loop is in an unoccupied
    cooling mode
    """

    pass


class Unoccupied_Heating_Mode_Status(Unoccupied_Mode_Status, Heating_Mode_Status):
    """
    Indicates whether a system, device or control loop is in an unoccupied
    heating mode
    """

    pass


class Zone_Air_Conditioning_Mode_Status(Mode_Status):
    """
    Indicates the mode of AC for a zone
    """

    pass


class Occupancy_Status(Status):
    """
    Indicates if a room or space is occupied
    """

    pass


class Temporary_Occupancy_Status(Occupancy_Status):
    """
    For systems that differentiate between scheduled occupied/unoccupied
    mode, this indicates if a space is temporarily occupied when it would
    otherwise be unoccupied
    """

    pass


class Off_Status(Status):
    """
    Indicates if a control loop, relay or equipment is off
    """

    pass


class On_Status(Status):
    """
    Indicates if a control loop, relay or equipment is on
    """

    pass


class On_Off_Status(Off_Status, On_Status, Status):
    """
    Indicates the on/off status of a control loop, relay or equipment
    """

    pass


class Fan_On_Off_Status(On_Off_Status, Fan_Status):
    pass


class Locally_On_Off_Status(On_Off_Status):
    pass


class Motor_On_Off_Status(On_Off_Status):
    pass


class Pump_On_Off_Status(On_Off_Status):
    pass


class Remotely_On_Off_Status(On_Off_Status):
    pass


class Standby_Unit_On_Off_Status(On_Off_Status):
    """
    Indicates the on/off status of a standby unit
    """

    pass


class Standby_Glycool_Unit_On_Off_Status(Standby_Unit_On_Off_Status):
    """
    Indicates the on/off status of a standby glycool unit
    """

    pass


class Start_Stop_Status(On_Off_Status):
    """
    Indicates the active/inactive status of a control loop (but not
    equipment activities or relays -- use On/Off for this purpose)
    """

    pass


class Cooling_Start_Stop_Status(Start_Stop_Status):
    pass


class Dehumidification_Start_Stop_Status(Start_Stop_Status):
    pass


class EconCycle_Start_Stop_Status(Start_Stop_Status):
    pass


class Heating_Start_Stop_Status(Start_Stop_Status):
    pass


class Humidification_Start_Stop_Status(Start_Stop_Status):
    pass


class Run_Status(Start_Stop_Status):
    pass


class Run_Request_Status(Run_Status):
    """
    Indicates if a request has been filed to start a device or equipment
    """

    pass


class Open_Close_Status(Status):
    """
    Indicates the open/close status of a device such as a damper or valve
    """

    pass


class Overridden_Status(Status):
    """
    Indicates if the expected operating status of an equipment or control
    loop has been overridden
    """

    pass


class Overridden_Off_Status(Off_Status, Overridden_Status):
    """
    Indicates if a control loop, relay or equipment has been turned off
    when it would otherwise be scheduled to be on
    """

    pass


class Overridden_On_Status(Overridden_Status, On_Status):
    """
    Indicates if a control loop, relay or equipment has been turned on
    when it would otherwise be scheduled to be off
    """

    pass


class Pressure_Status(Status):
    """
    Indicates if pressure is within expected bounds
    """

    pass


class Differential_Pressure_Load_Shed_Status(Pressure_Status, Load_Shed_Status):
    pass


class Chilled_Water_Differential_Pressure_Load_Shed_Status(
    Differential_Pressure_Load_Shed_Status
):
    pass


class Chilled_Water_Differential_Pressure_Load_Shed_Reset_Status(
    Chilled_Water_Differential_Pressure_Load_Shed_Status
):
    pass


class Hot_Water_Differential_Pressure_Load_Shed_Status(
    Differential_Pressure_Load_Shed_Status
):
    pass


class Hot_Water_Differential_Pressure_Load_Shed_Reset_Status(
    Hot_Water_Differential_Pressure_Load_Shed_Status
):
    pass


class Medium_Temperature_Hot_Water_Differential_Pressure_Load_Shed_Status(
    Differential_Pressure_Load_Shed_Status
):
    pass


class Medium_Temperature_Hot_Water_Differential_Pressure_Load_Shed_Reset_Status(
    Medium_Temperature_Hot_Water_Differential_Pressure_Load_Shed_Status
):
    pass


class Discharge_Air_Duct_Pressure_Status(Pressure_Status):
    """
    Indicates if air pressure in discharge duct is within expected bounds
    """

    pass


class Supply_Air_Duct_Pressure_Status(Pressure_Status):
    """
    Indicates if air pressure in supply duct is within expected bounds
    """

    pass


class Pump_Status(Status):
    """
    Status of a pump
    """

    pass


class Speed_Status(Status):
    pass


class Stages_Status(Status):
    """
    Indicates which stage a control loop or equipment is in
    """

    pass


class Switch_Status(Status):
    """
    Status of a switch
    """

    pass


class System_Status(Status):
    """
    Indicates properties of the activity of a system
    """

    pass


class Emergency_Air_Flow_System_Status(System_Status):
    pass


class Emergency_Power_Off_System_Status(System_Status, Off_Status):
    pass


class Emergency_Power_Off_System_Activated_By_High_Temperature_Status(
    Emergency_Power_Off_System_Status
):
    pass


class Emergency_Power_Off_System_Activated_By_Leak_Detection_System_Status(
    Emergency_Power_Off_System_Status
):
    pass


class Heat_Exchanger_System_Enable_Status(System_Status, Enable_Status):
    """
    Indicates if the heat exchanger system has been enabled
    """

    pass


class System_Shutdown_Status(System_Status, Status):
    """
    Indicates if a system has been shutdown
    """

    pass


class Thermostat_Status(Status):
    """
    Status of a thermostat
    """

    pass


class Tint_Status(Status):
    """
    The current level of window tint, errors, or transient states.
    """

    pass


class Valve_Status(Status):
    """
    The current status of the valve.
    """

    pass


class Tag(Entity):
    pass


class Relationship:
    """
    Super-property of all Brick relationships between entities (Equipment,
    Location, Point)
    """

    pass


class EntityProperty(Relationship):
    pass
