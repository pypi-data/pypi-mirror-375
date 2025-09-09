#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from hashlib import md5 as md5_hash
from soup_files import File, Directory, InputFiles, LibraryDocs, ProgressBarAdapter
from io import BytesIO
import numpy as np
from scipy.ndimage import uniform_filter
from convert_stream.enum_libs.enums import LibImage, RotationAngle
from convert_stream.enum_libs.modules import (
    MOD_IMG_PIL, ModuleImage, DEFAULT_LIB_IMAGE,
    cv2, MatLike, Image, ImageFilter
)


def get_hash_from_bytes(bt: BytesIO) -> str:
    return md5_hash(bt.getvalue()).hexdigest().upper()


class ABCImageObject(ABC):

    def __init__(self, module_image: ModuleImage, name: str) -> None:
        self.max_size: tuple[int, int] = (1980, 720) # Dimensões máximas, altere se necessário.
        self.module_image: ModuleImage = module_image
        self.lib_image: LibImage = LibImage.OPENCV
        self.name: str = name

    @abstractmethod
    def get_dimensions(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def is_landscape(self) -> bool:
        """Verificar se a imagen é do tipo paisagem"""
        pass

    @abstractmethod
    def is_vertical(self) -> bool:
        pass

    @abstractmethod
    def set_landscape(self):
        pass

    @abstractmethod
    def set_vertical(self):
        pass

    @abstractmethod
    def set_rotation(self, angle: RotationAngle) -> None:
        pass

    @abstractmethod
    def set_gausian_blur(self, sigma: float = 0.7):
        pass

    @abstractmethod
    def set_background_blur(self, sigma: float):
        pass

    @abstractmethod
    def set_background_black(self):
        pass

    @abstractmethod
    def set_background_gray(self):
        pass

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> BytesIO:
        pass

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        pass

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        pass


class ImplementOpenCv(ABCImageObject):
    def __init__(self, module_image: ModuleImage, name: str) -> None:
        super().__init__(module_image, name)
        self.lib_image = LibImage.OPENCV

        # Redimensionar se necessário
        dimensions = (self.module_image.shape[1], self.module_image.shape[0])  # (largura, altura)
        if (dimensions[0] > self.max_size[0]) or (dimensions[1] > self.max_size[1]):
            h, w = self.module_image.shape[:2]
            scale = min(self.max_size[0] / w, self.max_size[1] / h)
            new_size = (int(w * scale), int(h * scale))
            self.module_image = cv2.resize(self.module_image, new_size, interpolation=cv2.INTER_LANCZOS4)

    def get_dimensions(self) -> tuple[int, int]:
        height, width = self.module_image.shape[:2]
        return width, height

    def is_landscape(self) -> bool:
        w, h = self.get_dimensions()
        return w > h

    def is_vertical(self) -> bool:
        w, h = self.get_dimensions()
        return h > w

    def set_landscape(self):
        if self.is_vertical():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_vertical(self):
        if self.is_landscape():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_rotation(self, angle: RotationAngle) -> None:
        if angle == RotationAngle.ROTATION_90:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == RotationAngle.ROTATION_180:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_180)
        elif angle == RotationAngle.ROTATION_270:
            self.module_image = cv2.rotate(self.module_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    def set_gausian_blur(self, sigma: float = 0.7):
        # 1. Converte para escala de cinza
        gray = cv2.cvtColor(self.module_image, cv2.COLOR_BGR2GRAY)

        # 2. Detecta o texto com threshold adaptativo
        #    Texto ficará branco (255) e fundo preto (0)
        text_mask = cv2.adaptiveThreshold(
            gray, 160,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            25, 15
        )

        # 3. Inverte máscara (fundo branco, texto preto)
        background_mask = cv2.bitwise_not(text_mask)

        # 4. Borra apenas o fundo
        blurred_background = cv2.GaussianBlur(gray, (0, 0), sigma)

        # 5. Combina: fundo borrado + texto nítido
        text_part = cv2.bitwise_and(gray, gray, mask=text_mask)
        background_part = cv2.bitwise_and(blurred_background, blurred_background, mask=background_mask)
        combined = cv2.add(text_part, background_part)

        # 6. Realça contraste (texto mais escuro, fundo mais claro)
        combined = cv2.normalize(combined, None, 0, 255, cv2.NORM_MINMAX)
        combined = cv2.convertScaleAbs(combined, alpha=1.5, beta=20)

        # 7. Salva de volta em BGR
        self.module_image = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)

    def set_background_blur(self, sigma: float):
        # 1. Converter para escala de cinza
        gray = cv2.cvtColor(self.module_image, cv2.COLOR_BGR2GRAY)

        # 2. Borramento para capturar apenas o fundo suave
        blur = cv2.GaussianBlur(gray, (0, 0), sigma)

        # 3. Subtração para aumentar contraste do texto
        enhanced = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)

        # 4. Normalizar (clarear fundo, escurecer texto)
        norm = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)

        # 5. Converter de volta para BGR
        self.module_image = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)

    def set_background_black(self):
        mask = cv2.cvtColor(self.module_image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        self.module_image = cv2.bitwise_and(self.module_image, self.module_image, mask=mask_inv)

    def set_background_gray(self):
        # 1. Converte para escala de cinza
        gray = cv2.cvtColor(self.module_image, cv2.COLOR_BGR2GRAY)

        # 2. Detecta o texto (texto=branco, fundo=preto)
        text_mask = cv2.adaptiveThreshold(
            gray, 200,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            25, 15
        )

        # 3. Inverte máscara para pegar fundo
        background_mask = cv2.bitwise_not(text_mask)

        # 4. Cria fundo uniforme cinza claro
        gray_bg_value = 200  # tom claro de cinza (0=preto, 255=branco)
        background = np.full_like(gray, gray_bg_value, dtype=np.uint8)

        # 5. Deixa texto bem escuro
        text_dark_value = 30
        text_layer = np.full_like(gray, text_dark_value, dtype=np.uint8)

        # 6. Combina texto escuro com fundo cinza
        text_part = cv2.bitwise_and(text_layer, text_layer, mask=text_mask)
        background_part = cv2.bitwise_and(background, background, mask=background_mask)
        combined = cv2.add(text_part, background_part)

        # 7. Salva em BGR
        self.module_image = cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR)

    def to_file(self, file: File):
        #print(f'Exportando arquivo: {file.basename()}')
        cv2.imwrite(file.absolute(), self.module_image)

    def to_bytes(self) -> BytesIO:
        # Codifica como PNG em memória
        success, buffer = cv2.imencode(".png", self.module_image)
        if not success:
            raise ValueError("Falha ao converter a imagem para bytes.")
        output = BytesIO(buffer.tobytes())
        return output

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        img = cv2.imread(f.absolute())
        if img is None:
            raise ValueError(f"Não foi possível abrir a imagem: {f.absolute()}")
        return cls(img, f.name())

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        np_arr = np.frombuffer(bt, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Não foi possível criar a imagem a partir dos bytes fornecidos.")
        bytes_io = BytesIO(bt)
        name = get_hash_from_bytes(bytes_io)
        bytes_io.close()
        return cls(img, name)


class ImplementPIL(ABCImageObject):
    def __init__(self, module_image: ModuleImage, name: str):
        super().__init__(module_image, name)
        self.lib_image = LibImage.PIL

        # Redimensionar, se as dimensões estiverem maior que self.max_size.
        if (self.module_image.width > self.max_size[0]) or (self.module_image.height > self.max_size[1]):
            buff_image: BytesIO = BytesIO()
            self.module_image.save(buff_image, format='PNG', optimize=True, quality=90)
            self.module_image = Image.open(buff_image)
            buff_image.seek(0)
            #buff_image.close()
            #del buff_image
            #self.module_image.thumbnail(self.max_size, Image.LANCZOS)

    def get_dimensions(self) -> tuple[int, int]:
        return self.module_image.size  # (width, height)

    def is_landscape(self) -> bool:
        w, h = self.get_dimensions()
        return w > h

    def is_vertical(self) -> bool:
        w, h = self.get_dimensions()
        return h > w

    def set_landscape(self):
        if self.is_vertical():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_vertical(self):
        if self.is_landscape():
            self.set_rotation(RotationAngle.ROTATION_90)

    def set_rotation(self, angle: RotationAngle) -> None:
        self.module_image = self.module_image.rotate(
            -angle.value, expand=True
        )  # negativo = sentido horário

    def set_gausian_blur(self, sigma: float = 0.7):
        # 1. Converter para tons de cinza
        gray = self.module_image.convert("L")

        # 2. Borramento
        blur = gray.filter(ImageFilter.GaussianBlur(radius=sigma))

        # 3. Realçar texto combinando original e borrada
        np_gray = np.array(gray, dtype=np.float32)
        np_blur = np.array(blur, dtype=np.float32)
        enhanced = np.clip(1.5 * np_gray - 0.5 * np_blur, 0, 255).astype(np.uint8)

        # 4. Normalização
        min_val, max_val = enhanced.min(), enhanced.max()
        if max_val > min_val:
            enhanced = ((enhanced - min_val) * (255 / (max_val - min_val))).astype(np.uint8)

        # 5. Converter de volta para RGB
        self.module_image = Image.fromarray(enhanced).convert("RGB")

    def set_background_blur(self, sigma: float):
        # Converter para RGBA para preservar transparência
        img = self.module_image.convert("RGBA")

        # Criar versão borrada
        blurred = img.filter(ImageFilter.GaussianBlur(radius=sigma))

        # Criar máscara baseada na luminosidade
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p > 200 else 0).convert("1")

        # Combinar foreground com background borrado
        img.paste(blurred, mask=mask)
        self.module_image = img

    def set_background_black(self):
        img = self.module_image.convert("RGBA")
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p > 200 else 0).convert("1")
        black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
        img.paste(black_bg, mask=mask)
        self.module_image = img

    def set_background_gray(self):
        if not MOD_IMG_PIL:
            raise RuntimeError("PIL não está disponível.")

            # 1. Converte para escala de cinza
        gray_img = self.module_image.convert("L")

        # 2. Detecta o texto usando um threshold adaptativo (via NumPy)
        import numpy as np
        img_np = np.array(gray_img)

        # Parâmetros semelhantes ao adaptiveThreshold do OpenCV
        block_size = 25
        mean = uniform_filter(img_np.astype(np.float32), size=block_size)
        mask_text = (img_np < mean - 15).astype(np.uint8) * 255  # texto=255, fundo=0

        # 3. Máscara do fundo (inverso)
        mask_background = 255 - mask_text

        # 4. Cria fundo cinza claro
        gray_bg_value = 200
        background_np = np.full_like(img_np, gray_bg_value, dtype=np.uint8)

        # 5. Texto escuro
        text_dark_value = 30
        text_np = np.full_like(img_np, text_dark_value, dtype=np.uint8)

        # 6. Combina texto escuro com fundo cinza
        combined_np = ((text_np * (mask_text // 255)) +
                       (background_np * (mask_background // 255))).astype(np.uint8)

        # 7. Converte de volta para PIL (BGR → RGB não é necessário, pois estamos em L)
        self.module_image = Image.fromarray(combined_np).convert("RGB")

    def to_file(self, file: File) -> None:
        # Salva no formato original ou detectado pela extensão
        self.module_image.save(file.absolute())

    def to_bytes(self) -> BytesIO:
        buffer = BytesIO()
        # Tenta manter o formato original; se não houver, usa PNG
        fmt = self.module_image.format or "PNG"
        self.module_image.save(buffer, format=fmt)
        buffer.seek(0)
        return buffer

    @classmethod
    def create_from_file(cls, f: File) -> ABCImageObject:
        img = Image.open(f.path)
        return cls(img, f.name())

    @classmethod
    def create_from_bytes(cls, bt: bytes) -> ABCImageObject:
        img = Image.open(BytesIO(bt))
        bytes_io = BytesIO(bt)
        name = get_hash_from_bytes(bytes_io)
        bytes_io.close()
        return cls(img, name)


class ImageObject(object):

    def __init__(self, img_adapter: ABCImageObject) -> None:
        self.img_adapter: ABCImageObject = img_adapter
        self.name: str = img_adapter.name

    def to_pil(self) -> Image.Image:
        """
        Converte o ImageObject para um objeto PIL.Image.
        """
        # Obtém o stream de bytes da imagem
        image_bytes: BytesIO = self.to_bytes()
        # Cria e retorna um objeto Image do Pillow a partir do stream de bytes
        return Image.open(image_bytes)

    def to_opencv(self) -> MatLike:
        return cv2.imdecode(self.to_numpy(), cv2.IMREAD_COLOR)

    def to_numpy(self) -> np.ndarray:
        bt: BytesIO = self.to_bytes()
        return np.frombuffer(bt.getvalue(), np.uint8)

    def get_dimensions(self) -> tuple[int, int]:
        return self.img_adapter.get_dimensions()

    def is_landscape(self) -> bool:
        return self.img_adapter.is_landscape()

    def is_vertical(self) -> bool:
        return self.img_adapter.is_vertical()

    def set_landscape(self):
        return self.img_adapter.set_landscape()

    def set_vertical(self):
        return self.img_adapter.set_vertical()

    def set_rotation(self, angle: RotationAngle = RotationAngle.ROTATION_90) -> None:
        self.img_adapter.set_rotation(angle)

    def set_gausian_blur(self, sigma: float = 0.7):
        self.img_adapter.set_gausian_blur(sigma)

    def set_background_blur(self, sigma: float):
        self.img_adapter.set_background_blur(sigma)

    def set_background_black(self):
        self.img_adapter.set_background_black()

    def set_background_gray(self):
        self.img_adapter.set_background_gray()

    def to_file(self, file: File):
        self.img_adapter.to_file(file)

    def to_bytes(self) -> BytesIO:
        return self.img_adapter.to_bytes()

    @classmethod
    def create_from_file(cls, f: File, *, lib_image: LibImage = DEFAULT_LIB_IMAGE) -> ImageObject:
        if lib_image == LibImage.OPENCV:
            _adapter = ImplementOpenCv.create_from_file(f)
            return cls(_adapter)
        elif lib_image == LibImage.PIL:
            _adapter = ImplementPIL.create_from_file(f)
            return cls(_adapter)
        raise ValueError(f'Módulo imagem inválido: {lib_image}')

    @classmethod
    def create_from_bytes(cls, bt: bytes, *, lib_image: LibImage = DEFAULT_LIB_IMAGE) -> ImageObject:

        if lib_image == LibImage.OPENCV:
            _adapter = ImplementOpenCv.create_from_bytes(bt)
            return cls(_adapter)
        elif lib_image == LibImage.PIL:
            _adapter = ImplementPIL.create_from_bytes(bt)
            return cls(_adapter)
        raise ValueError(f'Módulo imagem inválido: {lib_image}')

    @classmethod
    def create_from_pil(cls, pil: ModuleImage) -> ImageObject:
        name = get_hash_from_bytes(BytesIO(pil.tobytes()))
        return cls(ImplementPIL(pil, name))


class CollectionImages(object):
    
    def __init__(self, images: list[ImageObject] = []) -> None:
        """

        :type images: list[ImageObject]
        """
        self.images: list[ImageObject] = images
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()
        self.__count: int = 0

    @property
    def length(self) -> int:
        return len(self.images)

    @property
    def is_empty(self) -> bool:
        return len(self.images) == 0

    def clear(self) -> None:
        self.images.clear()
        self.__count = 0

    def add_image(self, image: ImageObject) -> None:
        self.__count += 1
        self.pbar.update_text(f'Adicionando imagem {self.__count}')
        self.images.append(image)

    def add_file_image(self, file: File) -> None:
        self.pbar.start()
        self.__count += 1
        self.pbar.update_text(f'Adicionando imagem {self.__count} {file.basename()}')
        im = ImageObject.create_from_file(file)
        self.images.append(im)
        self.pbar.stop()

    def add_images(self, images: list[ImageObject]) -> None:
        for img in images:
            self.add_image(img)

    def add_files_image(self, files: list[File]) -> None:
        self.pbar.start()
        max_num: int = len(files)
        for num, f in enumerate(files):
            self.pbar.update(
                ((num+1) / max_num) * 100,
                f'Adicionando imagem: [{num+1} de {max_num}]'
            )
            self.images.append(ImageObject.create_from_file(f))
        self.pbar.stop()

    def add_directory_images(self, d: Directory, max_files: int = 4000) -> None:
        input_files = InputFiles(d, maxFiles=max_files)
        self.add_files_image(input_files.get_files(file_type=LibraryDocs.IMAGE))

    def to_files_image(
                self,
                output_dir: Directory,
                replace: bool = False,
                land_scape: bool = False,
                gaussian_filter: bool = False,
            ) -> None:
        self.pbar.start()
        print()
        output_dir.mkdir()
        max_num = len(self.images)
        for n, img in enumerate(self.images):
            filename = f'{img.name}.png'
            file_path = output_dir.join_file(filename)
            if (not replace) and (file_path.exists()):
                self.pbar.update_text(f'[PULANDO]: {file_path.basename()}')
                continue
            self.pbar.update(
                ((n + 1) / max_num) * 100,
                f'Exportando: [{n + 1} de {max_num}] {file_path.absolute()}',
            )
            if land_scape:
                img.set_landscape()
            if gaussian_filter:
                img.set_gausian_blur()
                img.set_background_gray()
            try:
                img.to_file(file_path)
            except Exception as e:
                print()
                self.pbar.update_text(f'{e}')
        self.pbar.stop()

    def set_land_scape(self):
        for im in self.images:
            im.set_landscape()

    def set_gausian_blur(self, sigma: float = 0.8) -> None:
        self.pbar.start()
        max_num: int = self.length
        for _num, im in enumerate(self.images):
            self.pbar.update(
                ((_num + 1) / max_num) * 100,
                f'Aplicando GausianBlur: [{_num + 1} de {max_num}]'
            )
            im.set_gausian_blur(sigma)
            im.set_background_gray()
        print()
        self.pbar.stop()

    def set_pbar(self, p: ProgressBarAdapter) -> None:
        self.pbar = p

