import { Detection } from "./detection";

export interface DetectionImage{
    name:string;
    detected:boolean;
    url:string;
}

export interface DetectionVideo{
    name:string;
    url:string;
}

export interface DetectionDetail extends Detection{
    images:DetectionImage[];
    video:DetectionVideo|null;
}