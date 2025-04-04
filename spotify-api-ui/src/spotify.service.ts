import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})

export class SpotifyService {
    private apiUrl = 'http://localhost:8888/callback';

    constructor(private http: HttpClient) {}

    getSongs(): Observable<any> {
        return this.http.get<any>(this.apiUrl);
    }
}