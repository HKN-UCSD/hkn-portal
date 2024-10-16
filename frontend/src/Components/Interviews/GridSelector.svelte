<script>
    export let onGridChange = (oldGrid, newGrid) => null;
    export let selectColor = "grey";
    export let unselectColor = "white";
    export let gridWidth = 3;
    export let gridHeight = 3;

    export let binaryData;
    export let startBit;

    let selectStart = null;

    console.log(`Created grid with width ${gridWidth} and height ${gridHeight}`);
    console.log(`Initial binary: ${binaryData}, at start bit ${startBit}`);

    // initialization
    let gridCoordToBitIdx = (x, y) => (x * gridHeight + y);
    let bitIdxToByte = (bitIdx) => (Math.trunc(bitIdx / 8));
    let bitIdxToByteMask = (bitIdx) => (0x80 >>> bitIdx % 8);
    let binaryToAvailabilityGrid = (binary, startBit) => createNewGrid(
        (x, y) => {
            let bitIdx = startBit + gridCoordToBitIdx(x, y);
            let byteIdx = bitIdxToByte(bitIdx);
            let byteMask = bitIdxToByteMask(bitIdx);
            let slotValue = binary[byteIdx] & byteMask;
            return slotValue != 0 ? true : false;
        }
    );

    // low-level helper funcs
    let createNewGrid = (itemAtCoordFunc) => {
        let newGrid = [];
        for (let h = 0; h < gridHeight; ++h) {
            newGrid.push([]);
            for (let w = 0; w < gridWidth; ++w) {
                newGrid[h].push(itemAtCoordFunc(w, h));
            }
        }
        return newGrid;
    }

    let mapGrid = (grid, itemAtCoordFunc) => {
        let newGrid = [];
        for (let h = 0; h < gridHeight; ++h) {
            newGrid.push([]);
            for (let w = 0; w < gridWidth; ++w) {
                newGrid[h].push(itemAtCoordFunc(grid, w, h));
            }
        }
        return newGrid;
    }

    let mapSubgrid = (grid, sX, sY, eX, eY, cb) => {
        let lowX = Math.min(sX, eX);
        let highX = Math.max(sX, eX);
        let lowY = Math.min(sY, eY);
        let highY = Math.max(sY, eY);
        return mapGrid(grid, (gridParam, x, y) => {
            if (lowX <= x && x <= highX && lowY <= y && y <= highY) {
                return cb(gridParam, x, y);
            }
            return gridParam[y][x];
        })
    }

    let fillSubgrid = (grid, sX, sY, eX, eY, fill) => {
        return mapSubgrid(grid, sX, sY, eX, eY, (grid, x, y) => fill);
    }

    // High-level implementation
    export let dataGrid = binaryToAvailabilityGrid(binaryData, startBit);
    let stagedGrid = binaryToAvailabilityGrid(binaryData, startBit);

    console.log(stagedGrid);

    $: colorGrid = mapGrid(stagedGrid, (grid, x, y) => {
        if (grid[y][x])
            return selectColor;
        return unselectColor;
    })

    let clickCbWrap = (x, y) => {
        if (selectStart === null) {
            selectStart = [x, y];
            onHover(x, y);
        } else {
            let oldGrid = dataGrid;
            dataGrid = stagedGrid;
            selectStart = null;
            onGridChange(oldGrid, dataGrid);
        }
    };

    let onHover = (x, y) => {
        if (selectStart != null) {
            let fill = !dataGrid[selectStart[1]][selectStart[0]];
            stagedGrid = fillSubgrid(dataGrid, selectStart[0], selectStart[1], x, y, fill);
        }
    }


</script>

<div class="avail-grid">
    {#each {length: gridWidth} as _, x (x)}
        {#each {length: gridHeight} as _, y (y)}
            <div 
                class="grid-block" 
                style="grid-area: {y + 1} / {x + 1};}" 
                on:click={() => clickCbWrap(x, y)} 
                on:mouseenter={() => onHover(x, y)}
            >
                <div class="grid-block-render" style="background-color: {colorGrid[y][x]};"></div>
            </div>
        {/each}
    {/each}
</div>

<style>
.avail-grid {
    display: grid;
    grid-auto-columns: 30px;
    grid-auto-rows: 10px;
    /*column-gap: 2px;*/
    /*row-gap: 2px;*/
}

.grid-block-render {
    width: 100%;
    height: 100%;
    border: 1px solid;
    border-color: var(--bordercol);
}
</style>
