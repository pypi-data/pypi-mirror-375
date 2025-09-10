from pyrilog import *
import os


def ensure_rtl_dir():
    """Ensure rtl directory exists"""
    os.makedirs("rtl", exist_ok=True)


def test_basic_module():
    """Test basic module generation"""
    print("=== Basic Module Test ===")
    with v_gen() as gen:
        with v_module("basic_module"):
            v_input("clk")
            v_input("rst")
            v_output("data", 8)
            v_wire("internal_signal", 16)
            v_reg("counter", 32)
            v_logic("control_signals", 4)

    with open("rtl/basic_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/basic_module.sv")


def test_multidimensional_arrays():
    """Test multidimensional array generation"""
    print("=== Multidimensional Arrays Test ===")
    with v_gen() as gen:
        with v_module("array_module"):
            v_input("clk")
            v_wire("mem", 8, [16, 4])  # 8-bit wide, 16x4 array
            v_reg("buffer", 1, 8)  # 1-bit wide, 8-element array (single int)
            v_reg("single_array", 4, 10)  # 4-bit wide, 10-element array (single int)
            v_output("data_out", 32, [2, 2])  # 32-bit wide, 2x2 array

    with open("rtl/array_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/array_module.sv")


def test_parameters_and_ports():
    """Test parameters and various port types with string var_type"""
    print("=== Parameters and Ports Test ===")
    with v_gen() as gen:
        with v_module("param_module"):
            v_param("WIDTH", "8")
            v_param("DEPTH", "16")

            v_input("clk")
            v_input("data_in", 8, None, "wire")
            v_output("data_out", 8, None, "reg")
            v_inout("bidir_port", 4, None, "wire")

    with open("rtl/param_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/param_module.sv")


def test_always_blocks():
    """Test always_ff and always_comb block generation"""
    print("=== Always Blocks Test ===")
    with v_gen() as gen:
        with v_module("always_module"):
            v_input("clk")
            v_input("rst_n")
            v_input("data_in", 8)
            v_output("q", 8, None, "reg")
            v_output("data_doubled", 8, None, "wire")

            # Sequential logic with always_ff
            with v_always_ff("clk", "rst_n"):
                with v_if("!rst_n"):
                    v_body("q <= 8'b0;")
                with v_else():
                    v_body("q <= data_in;")

            # Combinational logic with always_comb
            with v_always_comb():
                v_body("data_doubled = data_in << 1;")

    with open("rtl/always_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/always_module.sv")


def test_assignments():
    """Test assign statements"""
    print("=== Assignments Test ===")
    with v_gen() as gen:
        with v_module("assign_module"):
            v_input("a", 8)
            v_input("b", 8)
            v_output("sum", 9, None, "wire")
            v_wire("internal", 8, 4)  # Single dimension as int

            v_assign("sum", "a + b")
            v_assign("internal[0]", "a")
            v_assign("internal[1]", "b")

    with open("rtl/assign_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/assign_module.sv")


def test_instance():
    """Test module instantiation"""
    print("=== Instance Test ===")
    with v_gen() as gen:
        with v_module("top_module"):
            v_input("clk")
            v_input("data_in", 8)
            v_output("data_out", 8, None, "wire")

            v_inst(
                "memory_module",
                "mem_inst",
                {"WIDTH": "8", "DEPTH": "256"},
                {
                    "clk": "clk",
                    "addr": "addr",
                    "data_in": "data_in",
                    "data_out": "data_out",
                },
            )

    with open("rtl/top_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/top_module.sv")


def test_complex_module():
    """Test complex module with multiple features"""
    print("=== Complex Module Test ===")
    with v_gen() as gen:
        with v_module("complex_module"):
            # Parameters
            v_param("DATA_WIDTH", "32")
            v_param("ADDR_WIDTH", "10")

            # Ports
            v_input("clk")
            v_input("rst_n")
            v_input("wr_en")
            v_input("rd_en")
            v_input("addr", "ADDR_WIDTH")
            v_input("wr_data", "DATA_WIDTH")
            v_output("rd_data", "DATA_WIDTH", None, "reg")
            v_output("ready", 1, None, "reg")

            # Internal signals
            v_wire("mem_select")
            v_reg("state", 2)
            v_reg("memory", "DATA_WIDTH", ["2**ADDR_WIDTH"])
            v_logic("control_state", 4)

            v_newline()
            v_body("// State machine")
            with v_always_ff("clk", "rst_n"):
                with v_if("!rst_n"):
                    v_body("state <= 2'b00;")
                    v_body("ready <= 1'b0;")
                with v_else():
                    v_body("""case (state)
                                2'b00: begin
                                    if (wr_en) state <= 2'b01;
                                    else if (rd_en) state <= 2'b10;
                                end
                                2'b01: begin // Write state
                                    memory[addr] <= wr_data;
                                    ready <= 1'b1;
                                    state <= 2'b00;
                                end
                                2'b10: begin // Read state
                                    rd_data <= memory[addr];
                                    ready <= 1'b1;
                                    state <= 2'b00;
                                end
                                endcase""")

            v_newline()
            v_body("// Combinational logic")
            with v_always_comb():
                v_body("mem_select = wr_en | rd_en;")

    with open("rtl/complex_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/complex_module.sv")


def test_case_statements():
    """Test case statement generation"""
    print("=== Case Statement Test ===")
    with v_gen() as gen:
        with v_module("case_module"):
            v_input("clk")
            v_input("rst_n")
            v_input("opcode", 3)
            v_input("data_a", 8)
            v_input("data_b", 8)
            v_output("result", 8, None, "reg")
            v_output("valid", 1, None, "reg")

            with v_always_ff("clk", "rst_n"):
                with v_if("!rst_n"):
                    v_body("result <= 8'b0;")
                    v_body("valid <= 1'b0;")
                with v_else():
                    with v_case("opcode"):
                        # Single statement case items
                        v_case_item("3'b000", "result <= data_a + data_b;")
                        v_case_item("3'b001", "result <= data_a - data_b;")

                        # Multi-statement case items using context manager
                        with v_case_item("3'b010"):  # noqa: F405
                            v_body("result <= data_a & data_b;")
                            v_body("valid <= 1'b1;")

                        with v_case_item("3'b011"):
                            v_body("result <= data_a | data_b;")
                            v_body("valid <= 1'b1;")

                        # Single statement default
                        v_case_default("result <= 8'b0;")

                    v_body("valid <= 1'b1;")

    with open("rtl/case_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/case_module.sv")


def test_multi_module():
    """Test generating multiple modules in one file"""
    print("=== Multi-Module Test ===")
    with v_gen() as gen:
        # First module: Counter
        with v_module("counter"):
            v_param("WIDTH", "8")
            v_input("clk")
            v_input("rst_n")
            v_input("enable")
            v_output("count", "WIDTH", None, "reg")
            v_output("overflow", 1, None, "reg")
            
            with v_always_ff("clk", "rst_n"):
                with v_if("!rst_n"):
                    v_body("count <= {WIDTH{1'b0}};")
                    v_body("overflow <= 1'b0;")
                with v_else():
                    with v_if("enable"):
                        with v_if("count == {WIDTH{1'b1}}"):
                            v_body("count <= {WIDTH{1'b0}};")
                            v_body("overflow <= 1'b1;")
                        with v_else():
                            v_body("count <= count + 1'b1;")
                            v_body("overflow <= 1'b0;")
        
        # Second module: Decoder
        with v_module("decoder"):
            v_param("INPUT_WIDTH", "3")
            v_param("OUTPUT_WIDTH", "2**INPUT_WIDTH")
            v_input("in", "INPUT_WIDTH")
            v_input("enable")
            v_output("out", "OUTPUT_WIDTH", None, "reg")
            
            with v_always_comb():
                with v_if("enable"):
                    v_body("out = {OUTPUT_WIDTH{1'b0}};")
                    v_body("out[in] = 1'b1;")
                with v_else():
                    v_body("out = {OUTPUT_WIDTH{1'b0}};")
        
        # Third module: System combining both
        with v_module("counter_decoder_system"):
            v_input("clk")
            v_input("rst_n")
            v_input("enable")
            v_output("decoded_count", 8, None, "wire")
            v_output("overflow", 1, None, "wire")
            
            v_wire("counter_out", 3)
            
            v_newline()
            v_body("// Counter instance")
            v_inst("counter", "u_counter",
                   {"WIDTH": "3"},
                   {"clk": "clk", "rst_n": "rst_n", "enable": "enable", 
                    "count": "counter_out", "overflow": "overflow"})
            
            v_newline()
            v_body("// Decoder instance")
            v_inst("decoder", "u_decoder",
                   {"INPUT_WIDTH": "3", "OUTPUT_WIDTH": "8"},
                   {"in": "counter_out", "enable": "enable", "out": "decoded_count"})

    with open("rtl/multi_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/multi_module.sv")


def test_multiple_instances():
    """Test module instantiation with multiple instances"""
    print("=== Multiple Instances Test ===")
    with v_gen() as gen:
        with v_module("multi_instance_module"):
            v_input("clk")
            v_input("rst_n")
            v_input("data_in", 8)
            v_output("data_out", 8, None, "wire")
            v_wire("buffer_data", 8, 4)  # 4-element buffer
            
            v_newline()
            v_body("// Single instance (default count=1)")
            v_inst(
                "memory_module",
                "single_mem",
                {"WIDTH": "8", "DEPTH": "256"},
                {
                    "clk": "clk",
                    "rst_n": "rst_n", 
                    "data_in": "data_in",
                    "data_out": "data_out"
                }
            )
            
            v_newline()
            v_body("// Multiple instances with count parameter")
            v_inst(
                "buffer_module", 
                "mem_buffer",
                {"WIDTH": "8"},
                {
                    "clk": "clk",
                    "rst_n": "rst_n",
                    "data_in": "buffer_data",
                    "data_out": "buffer_data"
                },
                count=4
            )
            
            v_newline()
            v_body("// Large array of instances")
            v_inst(
                "processing_unit",
                "proc_units", 
                {"ID_WIDTH": "8"},
                {
                    "clk": "clk", 
                    "enable": "enable_array",
                    "data": "data_array"
                },
                count=16
            )
    
    with open("rtl/multi_instance_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/multi_instance_module.sv")


def test_logic_variables():
    """Test logic variable generation"""
    print("=== Logic Variables Test ===")
    with v_gen() as gen:
        with v_module("logic_test_module"):
            v_input("clk")
            v_input("rst_n")
            v_input("data_in", 8)
            v_output("data_out", 8, None, "logic")
            
            # Various logic declarations
            v_logic("single_bit")  # Default width=1
            v_logic("byte_signal", 8)  # 8-bit logic
            v_logic("word_signal", 32)  # 32-bit logic
            v_logic("array_signal", 4, 8)  # 4-bit wide, 8-element array
            v_logic("multi_dim", 8, [16, 4])  # 8-bit wide, 16x4 array
            
            with v_always_ff("clk", "rst_n"):
                with v_if("!rst_n"):
                    v_body("single_bit <= 1'b0;")
                    v_body("byte_signal <= 8'b0;")
                    v_body("word_signal <= 32'b0;")
                with v_else():
                    v_body("single_bit <= data_in[0];")
                    v_body("byte_signal <= data_in;")
                    v_body("word_signal <= {24'b0, data_in};")
            
            v_assign("data_out", "byte_signal")

    with open("rtl/logic_test_module.sv", "w") as f:
        f.write(gen.generate())
    print("Generated: rtl/logic_test_module.sv")


def test_error_handling():
    """Test error handling for invalid var_type"""
    print("=== Error Handling Test ===")
    try:
        with v_gen() as gen:
            with v_module("error_module"):
                v_input("clk", 1, None, "invalid_type")  # This should raise error
        print("ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")


def main():
    """Run all tests"""
    print("Pyrilog Generation Tests")
    print("=" * 50)
    print()

    ensure_rtl_dir()

    test_basic_module()
    test_multidimensional_arrays()
    test_parameters_and_ports()
    test_always_blocks()
    test_assignments()
    test_instance()
    test_multiple_instances()
    test_complex_module()
    test_case_statements()
    test_multi_module()
    test_logic_variables()
    # test_error_handling()

    print()
    print("All tests completed! Check rtl/ folder for generated SystemVerilog files.")


if __name__ == "__main__":
    main()
