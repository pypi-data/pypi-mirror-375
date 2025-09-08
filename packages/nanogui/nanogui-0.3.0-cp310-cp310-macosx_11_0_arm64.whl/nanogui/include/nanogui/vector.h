/*
    NanoGUI was developed by Wenzel Jakob <wenzel.jakob@epfl.ch>.
    The widget drawing code is based on the NanoVG demo application
    by Mikko Mononen.

    All rights reserved. Use of this source code is governed by a
    BSD-style license that can be found in the LICENSE.txt file.
*/

#pragma once

#include <nanogui/common.h>
#include <nanogui/traits.h>
#include <cmath>
#include <iosfwd>

NAMESPACE_BEGIN(nanogui)

template <typename Value_, size_t Size_> struct Array {
    static constexpr bool IsNanoGUI = true;
    static constexpr bool IsMatrix  = false;
    static constexpr size_t Size = Size_;
    using Value = Value_;

    Array() { }

    Array(const Array &) = default;
    Array& operator=(const Array &) = default;

    template <typename T,
              std::enable_if_t<T::Size == Size &&
                               std::is_same_v<typename T::Value, Value>, int> = 0>
    Array(const T &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] = (Value) a[i];
    }

    template <typename T>
    Array(const Array<T, Size> &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] = (Value) a.v[i];
    }

    Array(Value s) {
        for (size_t i = 0; i < Size; ++i)
            v[i] = s;
    }

    template <size_t S = Size, std::enable_if_t<S == 2, int> = 0>
    Array(Value v0, Value v1) {
        v[0] = v0; v[1] = v1;
    }

    template <size_t S = Size, std::enable_if_t<S == 3, int> = 0>
    Array(Value v0, Value v1, Value v2) {
        v[0] = v0; v[1] = v1; v[2] = v2;
    }

    template <size_t S = Size, std::enable_if_t<S == 4, int> = 0>
    Array(Value v0, Value v1, Value v2, Value v3) {
        v[0] = v0; v[1] = v1; v[2] = v2; v[3] = v3;
    }

    Array operator-() const {
        Array result;
        for (size_t i = 0; i < Size; ++i)
            result[i] = -v[i];
        return result;
    }

    friend Array operator+(const Array &a, const Array &b) {
        Array result;
        for (size_t i = 0; i < Size; ++i)
            result[i] = a.v[i] + b.v[i];
        return result;
    }

    Array& operator+=(const Array &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] += a.v[i];
        return *this;
    }

    friend Array operator-(const Array &a, const Array &b) {
        Array result;
        for (size_t i = 0; i < Size; ++i)
            result[i] = a.v[i] - b.v[i];
        return result;
    }

    Array& operator-=(const Array &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] -= a.v[i];
        return *this;
    }

    friend Array operator*(const Array &a, const Array &b) {
        Array result;
        for (size_t i = 0; i < Size; ++i)
            result[i] = a.v[i] * b.v[i];
        return result;
    }

    Array& operator*=(const Array &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] *= a.v[i];
        return *this;
    }

    friend Array operator/(const Array &a, const Array &b) {
        Array result;
        for (size_t i = 0; i < Size; ++i)
            result[i] = a.v[i] / b.v[i];
        return result;
    }

    Array& operator/=(const Array &a) {
        for (size_t i = 0; i < Size; ++i)
            v[i] /= a.v[i];
        return *this;
    }

    bool operator==(const Array &a) const {
        for (size_t i = 0; i < Size; ++i) {
            if (v[i] != a.v[i])
                return false;
        }
        return true;
    }

    bool operator!=(const Array &a) const {
        return !operator==(a);
    }

    const Value &operator[](size_t i) const {
        assert(i < Size);
        return v[i];
    }

    Value &operator[](size_t i) {
        assert(i < Size);
        return v[i];
    }

    Value *data() { return v; }
    const Value *data() const { return v; }

    template <size_t S = Size, std::enable_if_t<(S >= 1), int> = 0>
    const Value &x() const { return v[0]; }
    template <size_t S = Size, std::enable_if_t<(S >= 1), int> = 0>
    Value &x() { return v[0]; }

    template <size_t S = Size, std::enable_if_t<(S >= 2), int> = 0>
    const Value &y() const { return v[1]; }
    template <size_t S = Size, std::enable_if_t<(S >= 2), int> = 0>
    Value &y() { return v[1]; }

    template <size_t S = Size, std::enable_if_t<(S >= 3), int> = 0>
    const Value &z() const { return v[2]; }
    template <size_t S = Size, std::enable_if_t<(S >= 3), int> = 0>
    Value &z() { return v[2]; }

    template <size_t S = Size, std::enable_if_t<(S >= 4), int> = 0>
    const Value &w() const { return v[3]; }
    template <size_t S = Size, std::enable_if_t<(S >= 4), int> = 0>
    Value &w() { return v[3]; }

    Value v[Size];
};

template <typename Value, size_t Size>
Value dot(const Array<Value, Size> &a1, const Array<Value, Size> &a2) {
    Value result = a1.v[0] * a2.v[0];
    for (size_t i = 1; i < Size; ++i)
        result += a1.v[i] * a2.v[i];
    return result;
}

template <typename Value, size_t Size>
Value squared_norm(const Array<Value, Size> &a) {
    Value result = a.v[0] * a.v[0];
    for (size_t i = 1; i < Size; ++i)
        result += a.v[i] * a.v[i];
    return result;
}

template <typename Value, size_t Size>
Value norm(const Array<Value, Size> &a) {
    return (Value) std::sqrt(squared_norm(a));
}

template <typename Value, size_t Size>
Array<Value, Size> normalize(const Array<Value, Size> &a) {
    return a / norm(a);
}

template <typename Value>
Array<Value, 3> cross(const Array<Value, 3> &a, const Array<Value, 3> &b) {
    return Array<Value, 3>(
        a.y()*b.z() - a.z()*b.y(),
        a.z()*b.x() - a.x()*b.z(),
        a.x()*b.y() - a.y()*b.x()
    );
}

template <typename T, std::enable_if_t<std::is_arithmetic_v<T>, int> = 0>
T min(T a, T b) { return a < b ? a : b; }

template <typename T, std::enable_if_t<std::is_arithmetic_v<T>, int> = 0>
T max(T a, T b) { return a > b ? a : b; }

template <typename T, std::enable_if_t<std::is_arithmetic_v<T>, int> = 0>
T clip(T val, T minval, T maxval) {
    if (val < minval)
        return minval;
    else if (val > maxval)
        return maxval;
    else
        return val;
}

template <typename Value, size_t Size>
Array<Value, Size> max(const Array<Value, Size> &a1, const Array<Value, Size> &a2) {
    Array<Value, Size> result;
    for (size_t i = 0; i < Size; ++i)
        result.v[i] = max(a1.v[i], a2.v[i]);
    return result;
}

template <typename Value, size_t Size>
Array<Value, Size> min(const Array<Value, Size> &a1, const Array<Value, Size> &a2) {
    Array<Value, Size> result;
    for (size_t i = 0; i < Size; ++i)
        result.v[i] = min(a1.v[i], a2.v[i]);
    return result;
}

template <typename Value, size_t Size>
Array<Value, Size> clip(const Array<Value, Size> &a1, const Array<Value, Size> &a2, const Array<Value, Size> &a3) {
    Array<Value, Size> result;
    for (size_t i = 0; i < Size; ++i)
        result.v[i] = clip(a1.v[i], a2.v[i], a3.v[i]);
    return result;
}

template <typename Value, size_t Size>
Array<Value, Size> inverse(const Array<Value, Size>& a) {
    Array<Value, Size> result;
    for (size_t i = 0; i < Size; ++i)
        result.v[i] = 1.0f / a.v[i];
    return result;
}

template <typename Value, size_t Size>
Value mean(const Array<Value, Size>& a) {
    Value result = 0;
    for (size_t i = 0; i < Size; ++i)
        result += a.v[i];
    return result / (Value)Size;
}

// Create aliases for common array types
using Vector2f = Array<float, 2>;
using Vector3f = Array<float, 3>;
using Vector4f = Array<float, 4>;
using Vector2i = Array<int32_t, 2>;
using Vector3i = Array<int32_t, 3>;
using Vector4i = Array<int32_t, 4>;

/**
 * \class Color common.h nanogui/common.h
 *
 * \brief Stores an RGBA floating point color value.
 *
 * This class simply wraps around an ``Vector4f``, providing some convenient
 * methods and terminology for thinking of it as a color.  The data operates in the
 * same way as ``Vector4f``, and the following values are identical:
 *
 * \rst
 * +---------+-------------+----------------+-------------+
 * | Channel | Array Index | Vector4f field | Color field |
 * +=========+=============+================+=============+
 * | Red     | ``0``       | x()            | r()         |
 * +---------+-------------+----------------+-------------+
 * | Green   | ``1``       | y()            | g()         |
 * +---------+-------------+----------------+-------------+
 * | Blue    | ``2``       | z()            | b()         |
 * +---------+-------------+----------------+-------------+
 * | Alpha   | ``3``       | w()            | a()         |
 * +---------+-------------+----------------+-------------+
 * \endrst
 */
class Color : public Vector4f {
public:
    using Vector4f::Vector4f;
    using Vector4f::operator=;

    /// Default constructor: represents black (``r, g, b, a = 0``)
    Color() : Color(0, 0, 0, 0) { }

    /// Initialize from a 4D vector
    Color(const Vector4f &color) : Vector4f(color) { }

    /**
     * Copies (x, y, z) from the input vector, and uses the value specified by
     * the ``alpha`` parameter for this Color object's alpha component.
     *
     * \param color
     * The three dimensional float vector being copied.
     *
     * \param alpha
     * The value to set this object's alpha component to.
     */
    Color(const Vector3f &color, float alpha)
        : Color(color[0], color[1], color[2], alpha) { }

    /**
     * Copies (x, y, z) from the input vector, casted as floats first and then
     * divided by ``255.0``, and uses the value specified by the ``alpha``
     * parameter, casted to a float and divided by ``255.0`` as well, for this
     * Color object's alpha component.
     *
     * \param color
     * The three dimensional integer vector being copied, will be divided by ``255.0``.
     *
     * \param alpha
     * The value to set this object's alpha component to, will be divided by ``255.0``.
     */
    Color(const Vector3i &color, int alpha)
        : Color(Vector3f(color) / 255.f, alpha / 255.f) { }

    /**
     * Copies (x, y, z) from the input vector, and sets the alpha of this color
     * to be ``1.0``.
     *
     * \param color
     * The three dimensional float vector being copied.
     */
    Color(const Vector3f &color) : Color(color, 1.0f) {}

    /**
     * Copies (x, y, z) from the input vector, casting to floats and dividing by
     * ``255.0``.  The alpha of this color will be set to ``1.0``.
     *
     * \param color
     * The three dimensional integer vector being copied, will be divided by ``255.0``.
     */
    Color(const Vector3i &color)
        : Color(Vector3f(color) / 255.f, 1.f) { }

    /**
     * Copies (x, y, z, w) from the input vector, casting to floats and dividing
     * by ``255.0``.
     *
     * \param color
     * The three dimensional integer vector being copied, will be divided by ``255.0``.
     */
    Color(const Vector4i &color)
        : Color(Vector4f(color) / 255.f) { }

    /**
     * Creates the Color ``(intensity, intensity, intensity, alpha)``.
     *
     * \param intensity
     * The value to be used for red, green, and blue.
     *
     * \param alpha
     * The alpha component of the color.
     */
    Color(float intensity, float alpha)
        : Color(Vector3f(intensity), alpha) { }

    /**
     * Creates the Color ``(intensity, intensity, intensity, alpha) / 255.0``.
     * Values are casted to floats before division.
     *
     * \param intensity
     * The value to be used for red, green, and blue, will be divided by ``255.0``.
     *
     * \param alpha
     * The alpha component of the color, will be divided by ``255.0``.
     */
    Color(int intensity, int alpha)
        : Color(Vector3i(intensity), alpha) { }

    /**
     * Explicit constructor: creates the Color ``(r, g, b, a)``.
     *
     * \param r
     * The red component of the color.
     *
     * \param g
     * The green component of the color.
     *
     * \param b
     * The blue component of the color.
     *
     * \param a
     * The alpha component of the color.
     */
    Color(float r, float g, float b, float a) : Color(Vector4f(r, g, b, a)) { }

    /**
     * Explicit constructor: creates the Color ``(r, g, b, a) / 255.0``.
     * Values are casted to floats before division.
     *
     * \param r
     * The red component of the color, will be divided by ``255.0``.
     *
     * \param g
     * The green component of the color, will be divided by ``255.0``.
     *
     * \param b
     * The blue component of the color, will be divided by ``255.0``.
     *
     * \param a
     * The alpha component of the color, will be divided by ``255.0``.
     */
    Color(int r, int g, int b, int a) : Color(Vector4f((float) r, (float) g, (float) b, (float) a) / 255.f) { }

    /// Return a reference to the red channel
    float &r() { return x(); }
    /// Return a reference to the red channel (const version)
    const float &r() const { return x(); }
    /// Return a reference to the green channel
    float &g() { return y(); }
    /// Return a reference to the green channel (const version)
    const float &g() const { return y(); }
    /// Return a reference to the blue channel
    float &b() { return z(); }
    /// Return a reference to the blue channel (const version)
    const float &b() const { return z(); }
    /// Return a reference to the alpha channel
    float &a() { return w(); }
    /// Return a reference to the alpha channel (const version)
    const float &a() const { return w(); }

    /**
     * Computes the luminance as ``l = 0.299r + 0.587g + 0.144b + 0.0a``.  If
     * the luminance is less than 0.5, white is returned.  If the luminance is
     * greater than or equal to 0.5, black is returned.  Both returns will have
     * an alpha component of 1.0.
     */
    Color contrasting_color() const {
        float luminance = dot(*this, Color(0.299f, 0.587f, 0.144f, 0.f));
        return Color(luminance < 0.5f ? 1.f : 0.f, 1.f);
    }

    /// Allows for conversion between this Color and NanoVG's representation.
    inline operator const NVGcolor &() const;
};

/// Simple matrix class with *column-major* storage (that is the convention used by OpenGL/Metal)
template <typename Value_, size_t Size_> struct Matrix {
    static constexpr bool IsNanoGUI = true;
    static constexpr bool IsMatrix  = true;

    using Value = Value_;
    static constexpr size_t Size = Size_;
    using Column = Array<Value, Size>;

    Matrix() { }

    explicit Matrix(Value s) {
        for (size_t i = 0; i < Size; ++i) {
            for (size_t j = 0; j < Size; ++j) {
                m[i][j] = i == j ? s : 0;
            }
        }
    }

    /// Initialize another matrix type
    template <typename Value2, size_t Size2>
    Matrix(const Matrix<Value2, Size2> &other) : Matrix(1.f) {
        for (size_t i = 0; i < std::min(Size, Size2); ++i) {
            for (size_t j = 0; j <  std::min(Size, Size2); ++j)
                m[i][j] = other.m[i][j];
        }
    }


    /// Initialize from sequence (in row-major order)
    template <typename... Args, std::enable_if_t<sizeof...(Args) == Size*Size, int> = 0>
    Matrix(Args... args) {
        Value data[] {(Value) args...};
        for (size_t i = 0; i < Size; ++i) {
            for (size_t j = 0; j < Size; ++j)
                m[i][j] = data[j*Size+i];
        }
    }

    /// Initialize from columns
    template <typename... Args, std::enable_if_t<std::conjunction_v<std::is_same<Args, Column>...>, int> = 0>
    Matrix(const Args&... args) : m{args...} { }

    friend Matrix operator*(const Matrix &a, const Matrix &b) {
        Matrix c;
        for (size_t i = 0; i < Size; ++i) {
            for (size_t j = 0; j < Size; ++j) {
                Value accum = 0;
                for (size_t k = 0; k < Size; ++k)
                    accum += a.m[k][i] * b.m[j][k];
                c.m[j][i] = accum;
            }
        }
        return c;
    }

    Matrix T() const {
        Matrix result;
        for (size_t i = 0; i < Size; ++i)
            for (size_t j = 0; j < Size; ++j)
                result.m[j][i] = m[i][j];
        return result;
    }

    static Matrix scale(const Array<Value, Size - 1> &v) {
        Matrix result;
        for (size_t i = 0; i < Size; ++i) {
            for (size_t j = 0; j < Size; ++j) {
                result.m[i][j] = i == j ? (i < Size - 1 ? v[i] : 1) : 0;
            }
        }
        return result;
    }

    static Matrix scale(const Array<Value, Size> &v) {
        Matrix result;
        for (size_t i = 0; i < Size; ++i) {
            for (size_t j = 0; j < Size; ++j) {
                result.m[i][j] = i == j ? v[i] : 0;
            }
        }
        return result;
    }

    static Matrix translate(const Array<Value, Size - 1> &v) {
        Matrix result(1.f);
        for (size_t i = 0; i < Size - 1; ++i)
            result.m[Size - 1][i] = v[i];
        return result;
    }

    template <size_t S = Size, std::enable_if_t<S == 4 || S == 3, int> = 0>
    static Matrix rotate(const Array<Value, 3> &axis, Value angle) {
        Value s = std::sin(angle),
              c = std::cos(angle),
              t = 1 - c;

        Matrix result(1.f);
        result.m[0][0] = c + axis.x() * axis.x() * t;
        result.m[1][1] = c + axis.y() * axis.y() * t;
        result.m[2][2] = c + axis.z() * axis.z() * t;

        Value tmp1 = axis.x() * axis.y() * t,
              tmp2 = axis.z() * s;
        result.m[0][1] = tmp1 + tmp2;
        result.m[1][0] = tmp1 - tmp2;

        tmp1 = axis.x() * axis.z() * t;
        tmp2 = axis.y() * s;
        result.m[0][2] = tmp1 - tmp2;
        result.m[2][0] = tmp1 + tmp2;

        tmp1 = axis.y() * axis.z() * t;
        tmp2 = axis.x() * s;
        result.m[1][2] = tmp1 + tmp2;
        result.m[2][1] = tmp1 - tmp2;

        return result;
    }

    template <size_t S = Size, std::enable_if_t<S == 4, int> = 0>
    static Matrix perspective(Value fov, Value near_, Value far_, Value aspect = 1.f) {
        Value recip = 1 / (near_ - far_),
              c     = 1 / std::tan(.5f * fov);

        Matrix trafo = Matrix::scale(Array<Value, Size>(c / aspect, c, (near_ + far_) * recip, 0.f));

        trafo.m[3][2] = 2.f * near_ * far_ * recip;
        trafo.m[2][3] = -1.f;

        return trafo;
    }

    template <size_t S = Size, std::enable_if_t<S == 4, int> = 0>
    static Matrix ortho(Value left, Value right,
                        Value bottom, Value top,
                        Value near_, Value far_) {

        Value rl = 1 / (right - left),
              tb = 1 / (top - bottom),
              fn = 1 / (far_ - near_);

        Matrix result(0);

        result.m[0][0] = 2 * rl;
        result.m[1][1] = 2 * tb;
        result.m[2][2] = -2 * fn;
        result.m[3][3] = 1;
        result.m[3][0] = -(right + left) * rl;
        result.m[3][1] = -(top + bottom) * tb;
        result.m[3][2] = -(far_ + near_) * fn;

        return result;
    }

    template <size_t S = Size, std::enable_if_t<S == 4, int> = 0>
    static Matrix look_at(const Array<Value, 3> &origin,
                          const Array<Value, 3> &target,
                          const Array<Value, 3> &up) {

        auto dir = normalize(target - origin);
        auto left = normalize(cross(dir, up));
        auto new_up = cross(left, dir);
        dir = -dir;

        Matrix result(0);
        result.m[0][0] = left.x();
        result.m[0][1] = left.y();
        result.m[0][2] = left.z();
        result.m[1][0] = new_up.x();
        result.m[1][1] = new_up.y();
        result.m[1][2] = new_up.z();
        result.m[2][0] = dir.x();
        result.m[2][1] = dir.y();
        result.m[2][2] = dir.z();
        result.m[3][0] = -dot(left, origin);
        result.m[3][1] = -dot(new_up, origin);
        result.m[3][2] = -dot(dir, origin);
        result.m[3][3] = 1.f;
        return result;
    }

    Column &operator[](size_t i) { return m[i]; }
    const Column &operator[](size_t i) const { return m[i]; }

    Column m[Size];
};

using Matrix2f = Matrix<float, 2>;
using Matrix3f = Matrix<float, 3>;
using Matrix4f = Matrix<float, 4>;

inline Matrix3f inverse(const Matrix3f& mat) {
    float d11 = mat.m[1][1] * mat.m[2][2] + mat.m[1][2] * -mat.m[2][1];
    float d12 = mat.m[1][0] * mat.m[2][2] + mat.m[1][2] * -mat.m[2][0];
    float d13 = mat.m[1][0] * mat.m[2][1] + mat.m[1][1] * -mat.m[2][0];

    float det = mat.m[0][0] * d11 - mat.m[0][1] * d12 + mat.m[0][2] * d13;

    if (std::abs(det) == 0.0f) {
        return Matrix3f{0.0f};
    }

    det = 1.0f / det;

    float d21 = mat.m[0][1] * mat.m[2][2] + mat.m[0][2] * -mat.m[2][1];
    float d22 = mat.m[0][0] * mat.m[2][2] + mat.m[0][2] * -mat.m[2][0];
    float d23 = mat.m[0][0] * mat.m[2][1] + mat.m[0][1] * -mat.m[2][0];

    float d31 = mat.m[0][1] * mat.m[1][2] - mat.m[0][2] * mat.m[1][1];
    float d32 = mat.m[0][0] * mat.m[1][2] - mat.m[0][2] * mat.m[1][0];
    float d33 = mat.m[0][0] * mat.m[1][1] - mat.m[0][1] * mat.m[1][0];

    Matrix3f result;
    result.m[0][0] = +d11 * det;
    result.m[0][1] = -d21 * det;
    result.m[0][2] = +d31 * det;
    result.m[1][0] = -d12 * det;
    result.m[1][1] = +d22 * det;
    result.m[1][2] = -d32 * det;
    result.m[2][0] = +d13 * det;
    result.m[2][1] = -d23 * det;
    result.m[2][2] = +d33 * det;

    return result;
}

inline Matrix3f transpose(const Matrix3f& mat) {
    Matrix3f result;
    for (int m = 0; m < 3; ++m) {
        for (int n = 0; n < 3; ++n) {
            result.m[m][n] = mat.m[n][m];
        }
    }

    return result;
}

template <typename Value, size_t Size> Array<Value, Size> operator*(const Matrix<Value, Size>& m, const Array<Value, Size>& v) {
    Array<Value, Size> result;
    for (size_t i = 0; i < Size; ++i) {
        Value accum = 0;
        for (size_t k = 0; k < Size; ++k) {
            accum += m.m[k][i] * v.v[k];
        }

        result.v[i] = accum;
    }

    return result;
}

template <typename Value, size_t Size> Array<Value, Size - 1> operator*(const Matrix<Value, Size>& m, const Array<Value, Size - 1>& v) {
    Array<Value, Size - 1> result;
    Value w = 0;
    for (size_t i = 0; i < Size; ++i) {
        Value accum = 0;
        for (size_t k = 0; k < Size; ++k) {
            accum += m.m[k][i] * (k == Size - 1 ? 1 : v.v[k]);
        }

        if (i == Size - 1) {
            w = accum;
        } else {
            result.v[i] = accum;
        }
    }

    return result / w;
}

template <typename Value, size_t Size> bool operator==(const Matrix<Value, Size>& a, const Matrix<Value, Size>& b) {
    for (size_t m = 0; m < Size; ++m) {
        for (size_t n = 0; n < Size; ++n) {
            if (a.m[m][n] != b.m[m][n]) {
                return false;
            }
        }
    }

    return true;
}

template <typename Value, size_t Size> bool operator!=(const Matrix<Value, Size>& a, const Matrix<Value, Size>& b) { return !(a == b); }

template <typename Stream, typename Value, size_t Size,
          std::enable_if_t<std::is_base_of_v<std::ostream, Stream>, int> = 0>
Stream& operator<<(Stream &os, const Array<Value, Size> &v) {
    os << '[';
    for (size_t i = 0; i < Size; ++i) {
        os << v.v[i];
        if (i + 1 < Size)
            os << ", ";
    }
    os << ']';
    return os;
}

template <typename Stream, typename Value, size_t Size,
          std::enable_if_t<std::is_base_of_v<std::ostream, Stream>, int> = 0>
Stream& operator<<(Stream &os, const Matrix<Value, Size> &m) {
    os << '[';
    for (size_t i = 0; i < Size; ++i) {
        if (i != 0)
            os << ' ';
        os << '[';
        for (size_t j = 0; j < Size; ++j) {
            os << m.m[j][i];
            if (j + 1 < Size)
                os << ", ";
        }
        os << ']';
        if (i != Size -1)
            os << ",\n";
    }
    os << ']';
    return os;
}

NAMESPACE_END(nanogui)
