## AXI Stream

AMBA 4 interface specification is designed and published by ARM Ltd [@arm]. 
**AXI4-Stream** (AXIS) is an AMBA 4 protocol designed to transport streams of data of arbitrary widths (8n). 
Typically 32-bit wide buses are used, allowing 4 bytes to be transferred during one clock cycle. 
Many FPGA accelerators use AXIS to enable transformations of high throughput data streams. 
Typically a Direct Memory Access Controller (DMA) is used in conjunction with a processing system (PS) to move data between external memory such as DRAM and the accelerator (FPGA).

```wavedrom
{ signal: [
  {    name: 'aclk',   wave: 'p.............'},
  {    name: 'aresetn',   wave: '01............'},
  ['Master',
    ['ctrl',
        {name: 'strb', wave: '0.............'},
        {name: 'keep', wave: '0.............'},
        {name: 'id', wave: '0.............'},
        {name: 'dest', wave: '0.............'},
        {name: 'user', wave: '0.............'},
        {name: 'last', wave: '0......10.....'},
        {name: 'valid', wave: '0..1....0.....'},
    ],
    ['data',
        {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
    ]
  ],
  {},
  ['Slave',
    ['ctrl',
      {name: 'ready',   wave: '0.1..0.1......'},
    ],
    ['data',
        {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
    ]
  ]
],
head:{
   text:'AXI Stream Example',
   tick:0,
 },
 foot:{
   text:'Figure 1',
   tock:10
 },
config: { hscale: 1 }
}
```

### Data

**n** - Data bus width in bytes.

### ID

**i** - TID width. Recommended maximum is 8-bits.

### Dest

**d** - TDEST width. Recommended maximum is 4-bits.

### User

**u** - TUSER width. Recommended number of bits is an integer multiple of the width of the interface in bytes.



## AXI Full

TBD

## AXI Lite

TBD
