<style>
.layout {
    display: grid;

    /*Sizing and Spacing*/
    grid-template-columns: [availability-col] 2fr [title-col] 1fr;
    grid-template-rows: auto auto;
    column-gap: 10px;

    /*Areas*/
    grid-template-areas: 
        "availabilities title"
        "availabilities controls"
        ;
}

.avail-layout {
    display: grid;

    row-gap: 10px;
}

.title-block {
    grid-area: title;
}

.avail-layout {
    grid-area: availabilities;
}

.controls-block {
    grid-area: controls;
}


/*Mobile layout*/
@media (max-width: 50rem) {

    .layout {

        /*Sizing and Spacing*/
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
        column-gap: 10px;

        /*Areas*/
        grid-template-areas: 
            "title"
            "controls"
            "availabilities"
            ;

    }

}

</style>

<div class="layout">
    <div class="title-block">
        <slot name="title-block">Title block should go here.</slot>
    </div>
    <div class="avail-layout">
        <slot name="avail-layout">Availabilities should go here.</slot>
    </div>
    <div class="controls-block">
        <slot name="controls">Controls should go here.</slot>
    </div>
</div>
