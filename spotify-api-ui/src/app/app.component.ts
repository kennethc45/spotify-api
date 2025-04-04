import { Component, OnInit } from '@angular/core';
// import { RouterOutlet } from '@angular/router';
// import { SquareComponent } from "./square/square.component";
import { HttpClientModule } from '@angular/common/http';
import { SpotifyService } from '../spotify.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})

export class AppComponent implements OnInit {
  recentSongs: any;

  constructor(private spotifyService: SpotifyService) {}

  ngOnInit(): void {
    this.spotifyService.getSongs().subscribe(
      data => {
        this.recentSongs = data;
        console.log('Recent Songs:', this.recentSongs);
      },
      error => {
        console.error('app.component.ts unable to fetch songs:', error);
      }
    );
  }
}
