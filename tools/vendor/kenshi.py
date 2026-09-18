import struct


def flip_dict(input_dict):
    return {value: key for key, value in input_dict.items()}


EXTRA_ITEM_REMOVED = (2147483647, 2147483647, 2147483647)

FILE_TYPE = {
    15: "SAVE",
    16: "MOD"
}

FILE_TYPE_MAPPING = flip_dict(FILE_TYPE)

RECORD_DATATYPE = {
    -2147483646: "NEW",
    -2147483647: "CHANGED",
    -2147483645: "CHANGED_RENAMED"
}

RECORD_DATATYPE_MAPPING = flip_dict(RECORD_DATATYPE)

RECORD_TYPE = {
    0: "BUILDING",
    1: "CHARACTER",
    2: "WEAPON",
    3: "ARMOUR",
    4: "ITEM",
    5: "ANIMAL_ANIMATION",
    6: "ATTACHMENT",
    7: "RACE",
    9: "NATURE",
    10: "FACTION",
    13: "TOWN",
    16: "LOCATIONAL_DAMAGE",
    17: "COMBAT_TECHNIQUE",
    18: "DIALOGUE",
    19: "DIALOGUE_LINE",
    21: "RESEARCH",
    22: "AI_TASK",
    24: "ANIMATION",
    25: "STATS",
    26: "PERSONALITY",
    27: "CONSTANTS",
    28: "BIOMES",
    29: "BUILDING_PART",
    30: "INSTANCE_COLLECTION",
    31: "DIALOG_ACTION",
    34: "PLATOON",
    36: "GAMESTATE_CHARACTER",
    37: "GAMESTATE_FACTION",
    38: "GAMESTATE_TOWN_INSTANCE_LIST",
    41: "INVENTORY_STATE",
    42: "INVENTORY_ITEM_STATE",
    43: "REPEATABLE_BUILDING_PART_SLOT",
    44: "MATERIAL_SPEC",
    45: "MATERIAL_SPECS_COLLECTION",
    46: "CONTAINER",
    47: "MATERIAL_SPECS_CLOTHING",
    49: "VENDOR_LIST",
    50: "MATERIAL_SPECS_WEAPON",
    51: "WEAPON_MANUFACTURER",
    52: "SQUAD_TEMPLATE",
    53: "ROAD",
    55: "COLOR_DATA",
    56: "CAMERA",
    57: "MEDICAL_STATE",
    59: "FOLIAGE_LAYER",
    60: "FOLIAGE_MESH",
    61: "GRASS",
    62: "BUILDING_FUNCTIONALITY",
    63: "DAY_SCHEDULE",
    64: "NEW_GAME_STARTOFF",
    66: "CHARACTER_APPEARANCE",
    67: "GAMESTATE_AI",
    68: "WILDLIFE_BIRDS",
    69: "MAP_FEATURES",
    70: "DIPLOMATIC_ASSAULTS",
    71: "SINGLE_DIPLOMATIC_ASSAULT",
    72: "AI_PACKAGE",
    73: "DIALOGUE_PACKAGE",
    74: "GUN_DATA",
    76: "ANIMAL_CHARACTER",
    77: "UNIQUE_SQUAD_TEMPLATE",
    78: "FACTION_TEMPLATE",
    80: "WEATHER",
    81: "SEASON",
    82: "EFFECT",
    83: "ITEM_PLACEMENT_GROUP",
    84: "WORD_SWAPS",
    86: "NEST_ITEM",
    87: "CHARACTER_PHYSICS_ATTACHMENT",
    88: "LIGHT",
    89: "HEAD",
    92: "FOLIAGE_BUILDING",
    93: "FACTION_CAMPAIGN",
    94: "GAMESTATE_TOWN",
    95: "BIOME_GROUP",
    96: "EFFECT_FOG_VOLUME",
    97: "FARM_DATA",
    98: "FARM_PART",
    99: "ENVIRONMENT_RESOURCES",
    100: "RACE_GROUP",
    101: "ARTIFACTS",
    102: "MAP_ITEM",
    103: "BUILDINGS_SWAP",
    104: "ITEMS_CULTURE",
    105: "ANIMATION_EVENT",
    107: "CROSSBOW",
    109: "AMBIENT_SOUND",
    110: "WORLD_EVENT_STATE",
    111: "LIMB_REPLACEMENT",
    112: "BASE_ANIMATIONS"
}

RECORD_TYPE_MAPPING = flip_dict(RECORD_TYPE)


def get_file_type(type_id):
    try:
        return FILE_TYPE[type_id]
    except KeyError:
        return "UNKNOWN_FILE_TYPE[%d]" % type_id


def get_record_type(type_id):
    try:
        return RECORD_TYPE[type_id]
    except KeyError:
        return "UNKNOWN_RECORD_TYPE[%d]" % type_id


def get_record_datatype(type_id):
    try:
        return RECORD_DATATYPE[type_id]
    except KeyError:
        return "UNKNOWN_RECORD_DATATYPE[%d]" % type_id


class BinaryFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.handle = open(file_path, "rb")

    def int(self):
        binary = self.handle.read(4)
        return struct.unpack("i", binary)[0]

    def string(self):
        binary = self.handle.read(self.int())
        return binary.decode("utf-8")

    def char(self):
        binary = self.handle.read(1)
        return struct.unpack("c", binary)[0].decode("utf-8")

    def bool(self):
        binary = self.handle.read(1)
        return struct.unpack("?", binary)[0]

    def float(self):
        binary = self.handle.read(4)
        return struct.unpack("f", binary)[0]

    def vec3i(self):
        return self.int(), self.int(), self.int()

    def vec3f(self):
        return self.float(), self.float(), self.float()

    def vec4f(self):
        return self.float(), self.float(), self.float(), self.float()


class BinaryFileWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.handle = open(file_path, "wb")

    def int(self, value):
        self.handle.write(struct.pack("i", value))

    def string(self, value):
        encoded = value.encode('utf-8')
        self.int(len(encoded))
        self.handle.write(encoded)

    def char(self, value):
        self.handle.write(str.encode(value))

    def bool(self, value):
        self.handle.write(struct.pack("?", value))

    def float(self, value):
        self.handle.write(struct.pack("f", value))

    def vec3i(self, value):
        self.int(value[0])
        self.int(value[1])
        self.int(value[2])

    def vec3f(self, value):
        self.float(value[0])
        self.float(value[1])
        self.float(value[2])

    def vec4f(self, value):
        self.float(value[0])
        self.float(value[1])
        self.float(value[2])
        self.float(value[3])

    def filename(self, value):
        self.string(value)


class ModFileWriter(BinaryFileWriter):
    def __init__(self, file_path, version, author, description,
                 dependencies, references):
        super().__init__(file_path)
        self.int(FILE_TYPE_MAPPING["MOD"])
        self.int(version)
        self.string(author)
        self.string(description)
        self.string(dependencies)
        self.string(references)
        self.int(0)

    def records(self, records):
        self.int(len(records))
        for string_id, record in records.items():
            self.int(record["instance_count"])
            self.int(record["type_id"])
            self.int(record["id"])
            self.string(record["name"])
            self.string(string_id)
            self.int(record["datatype_id"])
            for field_type in ("bool", "float", "int", "vec3f", "vec4f",
                               "string", "filename"):
                self.fields(record["fields"][field_type], field_type)
            self.extra(record["extra"])
            self.instances(record["instances"])

    def extra(self, extra):
        self.int(len(extra))
        for extra_category, extra_fields in extra.items():
            self.string(extra_category)
            self.int(len(extra_fields))
            for field_name, field_value in extra_fields.items():
                self.string(field_name)
                self.vec3i(field_value)

    def fields(self, fields, field_type):
        self.int(len(fields))
        for field_name, field_value in fields.items():
            self.string(field_name)
            getattr(self, field_type)(field_value)

    def instances(self, instances):
        self.int(len(instances))
        for instance_id, instance_item in instances.items():
            self.string(instance_id)
            self.string(instance_item["target"])
            self.vec3f(instance_item["position"])
            self.vec4f(instance_item["rotation"])
            instance_states = instance_item["states"]
            self.int(len(instance_states))
            for instance_state in instance_states:
                self.string(instance_state)


class ModFileReader(BinaryFileReader):
    def __init__(self, file_path):
        super().__init__(file_path)

        file_type_id = self.int()
        self.file_type = 'MOD' if file_type_id == 17 else get_file_type(file_type_id)

        if self.file_type != "MOD":
            raise Exception("%s is not a mod file, %s found." % (
                file_path, self.file_type))

        header_end = None
        if file_type_id == 17:
            header_length = self.int()
            header_end = self.handle.tell() + header_length
        self.version = self.int()
        self.author = self.string()
        self.description = self.string()
        self.dependencies = self.string().split(",")
        self.references = self.string().split(",")
        if header_end is not None:
            self.handle.seek(header_end)
        self.flags = self.int()
        self.record_count = self.int()
        self.records = {}

        for _ in range(0, self.record_count):
            instance_count = self.int()
            record_type = self.int()
            record_id = self.int()
            name = self.string()
            string_id = self.string()
            datatype = self.int()
            fields_bool = self.fields(self.bool)
            fields_float = self.fields(self.float)
            fields_int = self.fields(self.int)
            fields_vec3f = self.fields(self.vec3f)
            fields_vec4f = self.fields(self.vec4f)
            fields_string = self.fields(self.string)
            fields_filename = self.fields(self.string)
            extra = self.extras()
            instances = self.instances()

            self.records[string_id] = {
                "instance_count": instance_count,
                "type_id": record_type,
                "type": get_record_type(record_type),
                "name": name,
                "id": record_id,
                "datatype_id": datatype,
                "datatype": ({0:'NEW',1:'CHANGED',2:'NEW',3:'CHANGED_RENAMED'}.get(datatype & 15, 'UNKNOWN') if file_type_id == 17 else get_record_datatype(datatype)),
                "fields": {
                    "bool": fields_bool,
                    "float": fields_float,
                    "int": fields_int,
                    "vec3f": fields_vec3f,
                    "vec4f": fields_vec4f,
                    "string": fields_string,
                    "filename": fields_filename,
                },
                "extra": extra,
                "instances": instances,
            }

    def fields(self, value_type):
        fields = {}
        for _ in range(0, self.int()):
            name = self.string()
            value = value_type()
            fields[name] = value
        return fields

    def extras(self):
        extras = {}
        length = self.int()
        for _ in range(0, length):
            name = self.string()
            extras[name] = self.extra_items()
        return extras

    def extra_items(self):
        items = {}
        length = self.int()
        for _ in range(0, length):
            name = self.string()
            value = self.vec3i()
            items[name] = value
        return items

    def instances(self):
        instances = {}
        length = self.int()
        for _ in range(0, length):
            instance_id = self.string()
            instances[instance_id] = {
                "target": self.string(),
                "position": self.vec3f(),
                "rotation": self.vec4f(),
                "states": self.instance_states()
            }
        return instances

    def instance_states(self):
        return [self.string() for _ in range(0, self.int())]


def is_renamed(record):
    return record['datatype'] == 'CHANGED_RENAMED'


def is_new(record):
    return record['datatype'] == 'NEW'


def merge_fields(record, old_record):
    for field_type, fields in record["fields"].items():
        for field_name, field_value in fields.items():
            old_record["fields"][field_type][
                field_name] = field_value


def merge_extra(record, old_record):
    for extra_category, items in record["extra"].items():
        if extra_category not in old_record["extra"]:
            old_record["extra"][extra_category] \
                = {}
        for item_name, item_value in items.items():
            if item_value == EXTRA_ITEM_REMOVED:
                old_record["extra"][
                    extra_category].pop(item_name, None)
            else:
                old_record["extra"][
                    extra_category][item_name] = item_value


def merge_records(mod_file, records):
    for string_id, record in mod_file.records.items():
        if string_id not in records:
            records[string_id] = record
        else:
            old_record = records[string_id]
            if is_new(record):
                raise Exception("Element %s from %s already exists."
                                % (string_id, mod_file.file_path))
            else:
                if is_renamed(record):
                    old_record["name"] = record["name"]

                merge_fields(record, old_record)
                merge_extra(record, old_record)
