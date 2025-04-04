import { Component, ChangeDetectorRef } from '@angular/core';

@Component({
    selector: 'app-square',
    standalone: true,   // Made square standalone so it can be directly imported in app.component
                        // IMPORTANT!!! - FILTERS SHOULD BE NON-STANDALONE SINCE THEY ARE GROUPTED 
                        // TOGETHER!!!
    template: `
        <p>
            square works!
            {{ rando }}
        </p>
    `,
    styles: []
})
export class SquareComponent {
    rando: number = Math.random();  

    // constructor() {
    //     setInterval(() => this.rando = Math.random(), 500);
    // }
    // constructor(private cdRef: ChangeDetectorRef) {
    //     setInterval(() => {
    //         this.rando = Math.random();
    //         this.cdRef.detectChanges(); 
    //     }, 500);
    // }
}