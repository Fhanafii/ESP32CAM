const API_URL = process.env.NEXT_PUBLIC_API_URL;

export function getFrameUrl(
    batchFolder:string,
    filename:string
){
    return `${API_URL}/api/files/${batchFolder}/${filename}`;
}

export function getVideoUrl(
    batchFolder:string,
    batchNumber:number
){
    return `${API_URL}/api/files/${batchFolder}/batch_${batchNumber}_detected.mp4`;
}