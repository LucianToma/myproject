/* Numere complexe și componente simetrice — folosit de motoarele de calcul ale modulelor.
   Rulează în browser (global CX) și în Node (module.exports), ca să poată fi verificat din teste. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CX = factory();
})(typeof self !== "undefined" ? self : this, function () {
  const C = (re, im = 0) => ({ re, im });
  const add = (...z) => z.reduce((a, b) => C(a.re + b.re, a.im + b.im), C(0));
  const sub = (a, b) => C(a.re - b.re, a.im - b.im);
  const mul = (a, b) => C(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re);
  const div = (a, b) => {
    const d = b.re * b.re + b.im * b.im;
    return C((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d);
  };
  const scale = (z, k) => C(z.re * k, z.im * k);
  const neg = (z) => C(-z.re, -z.im);
  const conj = (z) => C(z.re, -z.im);
  const abs = (z) => Math.hypot(z.re, z.im);
  const argDeg = (z) => (Math.atan2(z.im, z.re) * 180) / Math.PI;
  const polar = (m, deg) => C(m * Math.cos((deg * Math.PI) / 180), m * Math.sin((deg * Math.PI) / 180));
  const inv = (z) => div(C(1), z);
  const par = (a, b) => div(mul(a, b), add(a, b));
  /* operatorul a = 1∠120° */
  const A = polar(1, 120), A2 = polar(1, 240);
  /* [Ia Ib Ic] = [1 1 1; 1 a² a; 1 a a²]·[I0 I1 I2] */
  const seq2abc = (x0, x1, x2) => [
    add(x0, x1, x2),
    add(x0, mul(A2, x1), mul(A, x2)),
    add(x0, mul(A, x1), mul(A2, x2)),
  ];
  /* [I0 I1 I2] = 1/3·[1 1 1; 1 a a²; 1 a² a]·[Ia Ib Ic] */
  const abc2seq = (xa, xb, xc) => [
    scale(add(xa, xb, xc), 1 / 3),
    scale(add(xa, mul(A, xb), mul(A2, xc)), 1 / 3),
    scale(add(xa, mul(A2, xb), mul(A, xc)), 1 / 3),
  ];
  /* impedanță cu modul dat și raport R/X dat */
  const zRX = (Z, rx) => { const X = Z / Math.sqrt(1 + rx * rx); return C(rx * X, X); };
  return { C, add, sub, mul, div, scale, neg, conj, abs, argDeg, polar, inv, par, A, A2, seq2abc, abc2seq, zRX };
});
