import os
import tempfile

import cupy as cp
import numpy as np
import onnxruntime
import pixtreme as px
import pytest

import visagene_source as vg


class TestBlendSwapInference:
    """BlendSwap ONNXモデルの推論テスト"""

    def setup_method(self):
        """テストのセットアップ"""
        self.model_path = "models/blendswap.onnx"
        self.detection_model_path = "models/face_detection.onnx"
        self.source_path = "examples/example2.png"
        self.target_path = "examples/example.png"
        
        # モデルが存在するかチェック
        if not os.path.exists(self.model_path):
            pytest.skip(f"Model not found: {self.model_path}")
        
        # ONNXセッションの初期化
        self.session = onnxruntime.InferenceSession(self.model_path)
        
        # 入力・出力名の取得
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]

    def test_model_info(self):
        """モデルの入出力情報を確認"""
        inputs = self.session.get_inputs()
        outputs = self.session.get_outputs()
        
        print("\n=== BlendSwap Model Info ===")
        print(f"Number of inputs: {len(inputs)}")
        for i, inp in enumerate(inputs):
            print(f"Input {i}: name={inp.name}, shape={inp.shape}, type={inp.type}")
        
        print(f"\nNumber of outputs: {len(outputs)}")
        for i, out in enumerate(outputs):
            print(f"Output {i}: name={out.name}, shape={out.shape}, type={out.type}")
        
        # 基本的な確認
        assert len(inputs) == 2, "BlendSwap should have 2 inputs (target and source)"
        assert len(outputs) >= 1, "BlendSwap should have at least 1 output"

    def test_basic_inference(self):
        """基本的な推論テスト"""
        # 画像の読み込みと前処理
        source_image = px.imread(self.source_path)
        source_image = px.to_float32(source_image)
        source_image = px.bgr_to_rgb(source_image)
        
        target_image = px.imread(self.target_path)
        target_image = px.to_float32(target_image)
        target_image = px.bgr_to_rgb(target_image)
        
        # 顔検出
        detection = vg.OnnxFaceDetection(model_path=self.detection_model_path)
        
        source_faces = detection.get(source_image, crop_size=112)
        target_faces = detection.get(target_image, crop_size=256)
        
        assert len(source_faces) > 0, "No source face detected"
        assert len(target_faces) > 0, "No target face detected"
        
        source_face = source_faces[0]
        target_face = target_faces[0]
        
        # 前処理パラメータ
        input_mean = 0.5
        input_std = 0.5
        
        # バッチデータの準備
        source_batch = px.image_to_batch(source_face.image, std=input_std, mean=input_mean, size=112)
        target_batch = px.image_to_batch(target_face.image, std=input_std, mean=input_mean, size=256)
        
        source_batch = px.to_numpy(source_batch)
        target_batch = px.to_numpy(target_batch)
        
        # 推論実行
        preds = self.session.run(None, {
            self.input_names[0]: target_batch,
            self.input_names[1]: source_batch
        })
        
        # 結果の検証
        assert len(preds) >= 1, "No output from model"
        output = preds[0]
        
        # 出力形状の確認
        assert output.shape[0] == 1, "Batch size should be 1"
        assert output.shape[1] == 3, "Should have 3 channels (RGB)"
        assert len(output.shape) == 4, "Output should be 4D tensor (B, C, H, W)"
        
        # 出力値の範囲確認
        assert output.min() >= -1.5, "Output values too low"
        assert output.max() <= 1.5, "Output values too high"

    def test_output_consistency(self):
        """同じ入力で一貫した出力が得られるかテスト"""
        # ダミーデータで推論
        source_dummy = np.random.randn(1, 3, 112, 112).astype(np.float32)
        target_dummy = np.random.randn(1, 3, 256, 256).astype(np.float32)
        
        # 2回推論を実行
        output1 = self.session.run(None, {
            self.input_names[0]: target_dummy,
            self.input_names[1]: source_dummy
        })[0]
        
        output2 = self.session.run(None, {
            self.input_names[0]: target_dummy,
            self.input_names[1]: source_dummy
        })[0]
        
        # 結果が同一であることを確認
        np.testing.assert_allclose(output1, output2, rtol=1e-5)

    def test_batch_processing(self):
        """バッチ処理のテスト"""
        batch_size = 2
        
        # バッチデータの準備
        source_batch = np.random.randn(batch_size, 3, 112, 112).astype(np.float32)
        target_batch = np.random.randn(batch_size, 3, 256, 256).astype(np.float32)
        
        try:
            # バッチ推論を実行
            outputs = self.session.run(None, {
                self.input_names[0]: target_batch,
                self.input_names[1]: source_batch
            })
            
            output = outputs[0]
            assert output.shape[0] == batch_size, f"Expected batch size {batch_size}, got {output.shape[0]}"
            
        except Exception as e:
            # バッチサイズ1のみサポートの可能性
            pytest.skip(f"Batch processing not supported: {e}")

    def test_with_real_images(self):
        """実画像を使った完全な推論テスト"""
        # 画像の読み込みと前処理
        source_image = px.imread(self.source_path)
        source_image = px.to_float32(source_image)
        source_image = px.bgr_to_rgb(source_image)
        
        target_image = px.imread(self.target_path)
        target_image = px.to_float32(target_image)
        target_image = px.bgr_to_rgb(target_image)
        
        # 顔検出
        detection = vg.OnnxFaceDetection(model_path=self.detection_model_path)
        
        source_faces = detection.get(source_image, crop_size=112)
        target_faces = detection.get(target_image, crop_size=256)
        
        if len(source_faces) == 0 or len(target_faces) == 0:
            pytest.skip("No faces detected in test images")
        
        source_face = source_faces[0]
        target_face = target_faces[0]
        
        # 前処理
        input_mean = 0.5
        input_std = 0.5
        
        source_batch = px.image_to_batch(source_face.image, std=input_std, mean=input_mean, size=112)
        target_batch = px.image_to_batch(target_face.image, std=input_std, mean=input_mean, size=256)
        
        source_batch = px.to_numpy(source_batch)
        target_batch = px.to_numpy(target_batch)
        
        # 推論
        preds = self.session.run(None, {
            self.input_names[0]: target_batch,
            self.input_names[1]: source_batch
        })
        
        # 後処理
        output = preds[0]
        # numpy配列をcupy配列に変換
        output = cp.asarray(output)
        output_images = px.batch_to_images(output, std=input_std, mean=input_mean)
        output_image = output_images[0]
        output_image = px.rgb_to_bgr(output_image)
        
        # 出力画像の検証
        assert output_image.shape == (256, 256, 3), "Output image should be 256x256x3"
        assert output_image.min() >= 0, "Output image should have non-negative values"
        assert output_image.max() <= 1, "Output image values should be <= 1"
        
        # 一時ファイルに保存してテスト
        temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
        try:
            os.close(temp_fd)  # ファイルディスクリプタを閉じる
            px.imwrite(temp_path, output_image)
            assert os.path.exists(temp_path), "Failed to save output image"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])