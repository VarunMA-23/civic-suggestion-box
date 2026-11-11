'use client';

import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Camera, Loader2, X } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { civicAPI } from '@/lib/api';
import type { IdeaImage } from '@/types';

const MAX_IMAGES = 5;
const MAX_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

export function resolveUploadUrl(url: string): string {
  if (!url) return url;
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/uploads/')) return url;
  if (url.startsWith('data/uploads/')) {
    return `/uploads/${url.slice('data/uploads/'.length)}`;
  }
  if (url.startsWith('/data/uploads/')) {
    return `/uploads/${url.slice('/data/uploads/'.length)}`;
  }
  return url;
}

function validateFile(file: File): 'type' | 'size' | null {
  if (!ALLOWED_TYPES.includes(file.type)) return 'type';
  if (file.size > MAX_SIZE) return 'size';
  return null;
}

interface IdeaImageUploadProps {
  ideaId: number;
  images: IdeaImage[];
  onChange: (images: IdeaImage[]) => void;
  disabled?: boolean;
}

export function IdeaImageUpload({ ideaId, images, onChange, disabled }: IdeaImageUploadProps) {
  const { t } = useTranslation();
  const { error: showError } = useToast();
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    const remaining = MAX_IMAGES - images.length;
    if (remaining <= 0) {
      showError(t('civic.images.limitReached'), { isRaw: true });
      return;
    }

    const files = Array.from(fileList).slice(0, remaining);
    setUploading(true);
    const uploaded: IdeaImage[] = [];

    try {
      for (const file of files) {
        const problem = validateFile(file);
        if (problem === 'type') {
          showError(t('civic.images.invalidType'), { isRaw: true });
          continue;
        }
        if (problem === 'size') {
          showError(t('civic.images.tooLarge'), { isRaw: true });
          continue;
        }
        uploaded.push(await civicAPI.uploadImage(ideaId, file));
      }
      if (uploaded.length > 0) {
        onChange([...images, ...uploaded]);
      }
    } catch {
      showError(t('common.error'), { isRaw: true });
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const handleRemove = async (imageId: number) => {
    try {
      await civicAPI.deleteImage(ideaId, imageId);
      onChange(images.filter((image) => image.id !== imageId));
    } catch {
      showError(t('common.error'), { isRaw: true });
    }
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600 dark:text-gray-400">{t('civic.images.help')}</p>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {images.map((image) => (
          <div
            key={image.id}
            className="relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 group"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={resolveUploadUrl(image.url)}
              alt=""
              className="w-full h-full object-cover"
            />
            {!disabled && (
              <button
                type="button"
                onClick={() => handleRemove(image.id)}
                className="absolute top-1 right-1 p-1 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                aria-label={t('civic.images.remove')}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ))}

        {images.length < MAX_IMAGES && (
          <button
            type="button"
            disabled={disabled || uploading}
            onClick={() => inputRef.current?.click()}
            className="aspect-square rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 flex flex-col items-center justify-center gap-1 text-gray-500 dark:text-gray-400 hover:border-primary-500 hover:text-primary-600 transition-colors disabled:opacity-50"
          >
            {uploading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Camera className="w-5 h-5" />
            )}
            <span className="text-xs px-2 text-center">
              {uploading ? t('civic.images.uploading') : t('civic.images.add')}
            </span>
          </button>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(',')}
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}

interface ImageStagingProps {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
}

export function ImageStaging({ files, onChange, disabled }: ImageStagingProps) {
  const { t } = useTranslation();
  const { error: showError } = useToast();
  const inputRef = useRef<HTMLInputElement>(null);
  const previews = useRef(new Map<File, string>());

  const previewUrl = (file: File) => {
    let url = previews.current.get(file);
    if (!url) {
      url = URL.createObjectURL(file);
      previews.current.set(file, url);
    }
    return url;
  };

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    const remaining = MAX_IMAGES - files.length;
    if (remaining <= 0) {
      showError(t('civic.images.limitReached'), { isRaw: true });
      return;
    }

    const accepted: File[] = [];
    for (const file of Array.from(fileList).slice(0, remaining)) {
      const problem = validateFile(file);
      if (problem === 'type') {
        showError(t('civic.images.invalidType'), { isRaw: true });
        continue;
      }
      if (problem === 'size') {
        showError(t('civic.images.tooLarge'), { isRaw: true });
        continue;
      }
      accepted.push(file);
    }
    if (accepted.length > 0) onChange([...files, ...accepted]);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleRemove = (file: File) => {
    const url = previews.current.get(file);
    if (url) {
      URL.revokeObjectURL(url);
      previews.current.delete(file);
    }
    onChange(files.filter((item) => item !== file));
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600 dark:text-gray-400">{t('civic.images.help')}</p>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {files.map((file) => (
          <div
            key={`${file.name}-${file.lastModified}`}
            className="relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 group"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={previewUrl(file)} alt="" className="w-full h-full object-cover" />
            {!disabled && (
              <button
                type="button"
                onClick={() => handleRemove(file)}
                className="absolute top-1 right-1 p-1 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
                aria-label={t('civic.images.remove')}
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ))}

        {files.length < MAX_IMAGES && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => inputRef.current?.click()}
            className="aspect-square rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 flex flex-col items-center justify-center gap-1 text-gray-500 dark:text-gray-400 hover:border-primary-500 hover:text-primary-600 transition-colors disabled:opacity-50"
          >
            <Camera className="w-5 h-5" />
            <span className="text-xs px-2 text-center">{t('civic.images.add')}</span>
          </button>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(',')}
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}

export default IdeaImageUpload;
