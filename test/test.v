module blinky_zybo_z7
  #(parameter random = 16,
  parameter blah = 2)
  (input wire  clk,
   output wire q,
   input wire [random:(blah+random)] thing
   );

  //  wire        clk;

   blinky #(.clk_freq_hz (125_000_000)) blinky
     (.clk (clk),
      .q   (q));

endmodule

