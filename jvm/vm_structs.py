class MemoryUtil:
    # TODO: with debug symbols it should be easier
    # drop eval hacks
    @staticmethod
    def lookup_symbol_address(symbol):
        return int(gdb.parse_and_eval("(uint64_t) gHotSpotVMStructs"))

    @staticmethod
    def read_string_from_address(addr):
        # TODO: drop str dancing. It must be a easier waty to convert gbd.Value to string
        _, _, s = str(gdb.parse_and_eval("*(char**) %s" % addr)).partition(' "')
        return s[:-1]

    @staticmethod
    def read_long_from_symbol(symbol):
        return int(gdb.parse_and_eval("(unsigned long long) %s" % symbol))

    @staticmethod
    def read_ptr(addr):
        return int(gdb.parse_and_eval("* %d" % addr))


class VMStructs(gdb.Command):
    def __init__(self):
        super(VMStructs, self).__init__("vmstructs", gdb.COMMAND_USER)
        self._vmstructs_ready = False

    def _read_vmstructs(self):
        # look at vmStructs.hpp & vmStructs.cpp
        if self._vmstructs_ready:
            return

        self.VMStructsPtr = MemoryUtil.lookup_symbol_address("gHotSpotVMStructs")
        self.VMStructEntry_array_stride = MemoryUtil.read_long_from_symbol("gHotSpotVMStructEntryArrayStride")
        self.VMStructEntry_type_offset = MemoryUtil.read_long_from_symbol("gHotSpotVMStructEntryTypeNameOffset")
        self.VMStructEntry_fieldname_offset = MemoryUtil.read_long_from_symbol("gHotSpotVMStructEntryFieldNameOffset")
        self.VMStructEntry_offset_offset = MemoryUtil.read_long_from_symbol("gHotSpotVMStructEntryOffsetOffset")
        self.VMStructEntry_address_offset = MemoryUtil.read_long_from_symbol("gHotSpotVMStructEntryAddressOffset")
        self._vmstructs_ready = True

    def invoke(self, arg, from_tty):
        self._read_vmstructs()

        if self.VMStructsPtr == 0 or self.VMStructEntry_array_stride == 0:
            return
        
        pos = self.VMStructsPtr
        while True:
            if MemoryUtil.read_ptr(pos) == 0:
                return
            ttype = MemoryUtil.read_string_from_address(pos + self.VMStructEntry_type_offset)
            fieldname = MemoryUtil.read_string_from_address(pos + self.VMStructEntry_fieldname_offset)
            print("%s::%s" % (ttype, fieldname))

            pos += self.VMStructEntry_array_stride

VMStructs()