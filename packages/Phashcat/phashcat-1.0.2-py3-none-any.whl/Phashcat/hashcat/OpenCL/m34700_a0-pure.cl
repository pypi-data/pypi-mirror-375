/**
 * Author......: See docs/credits.txt
 * License.....: MIT
 */

//#define NEW_SIMD_CODE

#ifdef KERNEL_STATIC
#include M2S(INCLUDE_PATH/inc_vendor.h)
#include M2S(INCLUDE_PATH/inc_types.h)
#include M2S(INCLUDE_PATH/inc_platform.cl)
#include M2S(INCLUDE_PATH/inc_common.cl)
#include M2S(INCLUDE_PATH/inc_rp.h)
#include M2S(INCLUDE_PATH/inc_rp.cl)
#include M2S(INCLUDE_PATH/inc_scalar.cl)
#include M2S(INCLUDE_PATH/inc_hash_sha1.cl)
#include M2S(INCLUDE_PATH/inc_cipher_aes.cl)
#endif

DECLSPEC int is_valid_char (const u32 v)
{
  if ((v & 0xff000000) < 0x09000000) return 0;
  if ((v & 0xff000000) > 0x7e000000) return 0;
  if ((v & 0x00ff0000) < 0x00090000) return 0;
  if ((v & 0x00ff0000) > 0x007e0000) return 0;
  if ((v & 0x0000ff00) < 0x00000900) return 0;
  if ((v & 0x0000ff00) > 0x00007e00) return 0;
  if ((v & 0x000000ff) < 0x00000009) return 0;
  if ((v & 0x000000ff) > 0x0000007e) return 0;

  return 1;
}

KERNEL_FQ KERNEL_FA void m34700_mxx (KERN_ATTR_RULES ())
{
  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);
  const u64 lsz = get_local_size (0);

  /**
   * aes shared
   */

  #ifdef REAL_SHM

  LOCAL_VK u32 s_te0[256];
  LOCAL_VK u32 s_te1[256];
  LOCAL_VK u32 s_te2[256];
  LOCAL_VK u32 s_te3[256];
  LOCAL_VK u32 s_te4[256];

  for (u32 i = lid; i < 256; i += lsz)
  {
    s_te0[i] = te0[i];
    s_te1[i] = te1[i];
    s_te2[i] = te2[i];
    s_te3[i] = te3[i];
    s_te4[i] = te4[i];
  }

  SYNC_THREADS ();

  #else

  CONSTANT_AS u32a *s_te0 = te0;
  CONSTANT_AS u32a *s_te1 = te1;
  CONSTANT_AS u32a *s_te2 = te2;
  CONSTANT_AS u32a *s_te3 = te3;
  CONSTANT_AS u32a *s_te4 = te4;

  #endif

  if (gid >= GID_CNT) return;

  /**
   * CT
   */

  u32 iv[4];

  iv[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  iv[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  iv[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  iv[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  u32 ct[4];

  ct[0] = salt_bufs[SALT_POS_HOST].salt_buf[4];
  ct[1] = salt_bufs[SALT_POS_HOST].salt_buf[5];
  ct[2] = salt_bufs[SALT_POS_HOST].salt_buf[6];
  ct[3] = salt_bufs[SALT_POS_HOST].salt_buf[7];

  /**
   * base
   */

  COPY_PW (pws[gid]);

  /**
   * loop
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos++)
  {
    pw_t tmp = PASTE_PW;

    tmp.pw_len = apply_rules (rules_buf[il_pos].cmds, tmp.i, tmp.pw_len);

    u32 ukey[8];

    sha1_hmac_ctx_t sha1_hmac_ctx;

    sha1_hmac_init_swap (&sha1_hmac_ctx, tmp.i, tmp.pw_len);

    u32 w0[4];
    u32 w1[4];
    u32 w2[4];
    u32 w3[4];

    w0[0] = iv[0];
    w0[1] = iv[1];
    w0[2] = iv[2];
    w0[3] = iv[3];
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx, w0, w1, w2, w3, 16);

    sha1_hmac_ctx_t sha1_hmac_ctx2 = sha1_hmac_ctx;

    w0[0] = 1;
    w0[1] = 0;
    w0[2] = 0;
    w0[3] = 0;
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx2, w0, w1, w2, w3, 4);

    sha1_hmac_final (&sha1_hmac_ctx2);

    ukey[0] = sha1_hmac_ctx2.opad.h[0];
    ukey[1] = sha1_hmac_ctx2.opad.h[1];
    ukey[2] = sha1_hmac_ctx2.opad.h[2];
    ukey[3] = sha1_hmac_ctx2.opad.h[3];
    ukey[4] = sha1_hmac_ctx2.opad.h[4];

    sha1_hmac_ctx_t sha1_hmac_ctx3 = sha1_hmac_ctx;

    w0[0] = 2;
    w0[1] = 0;
    w0[2] = 0;
    w0[3] = 0;
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx3, w0, w1, w2, w3, 4);

    sha1_hmac_final (&sha1_hmac_ctx3);

    ukey[5] = sha1_hmac_ctx3.opad.h[0];
    ukey[6] = sha1_hmac_ctx3.opad.h[1];
    ukey[7] = sha1_hmac_ctx3.opad.h[2];

    #define KEYLEN 60

    u32 ks[KEYLEN];

    AES256_set_encrypt_key (ks, ukey, s_te0, s_te1, s_te2, s_te3);

    u32 out[4];

    AES256_encrypt (ks, iv, out, s_te0, s_te1, s_te2, s_te3, s_te4);

    u32 pt[4];

    pt[0] = ct[0] ^ out[0];
    pt[1] = ct[1] ^ out[1];
    pt[2] = ct[2] ^ out[2];
    pt[3] = ct[3] ^ out[3];

    if (is_valid_char (pt[0]) == 0) continue;
    if (is_valid_char (pt[1]) == 0) continue;
    if (is_valid_char (pt[2]) == 0) continue;
    if (is_valid_char (pt[3]) == 0) continue;

    int i;

    for (i = 8; i < 16; i += 4)
    {
      AES256_encrypt (ks, out, out, s_te0, s_te1, s_te2, s_te3, s_te4);

      pt[0] = salt_bufs[SALT_POS_HOST].salt_buf[i + 0] ^ out[0];
      pt[1] = salt_bufs[SALT_POS_HOST].salt_buf[i + 1] ^ out[1];
      pt[2] = salt_bufs[SALT_POS_HOST].salt_buf[i + 2] ^ out[2];
      pt[3] = salt_bufs[SALT_POS_HOST].salt_buf[i + 3] ^ out[3];

      if (is_valid_char (pt[0]) == 0) break;
      if (is_valid_char (pt[1]) == 0) break;
      if (is_valid_char (pt[2]) == 0) break;
      if (is_valid_char (pt[3]) == 0) break;
    }

    if (i < 16) continue;

    const u32 r0 = ct[0];
    const u32 r1 = ct[1];
    const u32 r2 = ct[2];
    const u32 r3 = ct[3];

    COMPARE_M_SCALAR (r0, r1, r2, r3);
  }
}

KERNEL_FQ KERNEL_FA void m34700_sxx (KERN_ATTR_RULES ())
{
  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);
  const u64 lsz = get_local_size (0);

  /**
   * aes shared
   */

  #ifdef REAL_SHM

  LOCAL_VK u32 s_te0[256];
  LOCAL_VK u32 s_te1[256];
  LOCAL_VK u32 s_te2[256];
  LOCAL_VK u32 s_te3[256];
  LOCAL_VK u32 s_te4[256];

  for (u32 i = lid; i < 256; i += lsz)
  {
    s_te0[i] = te0[i];
    s_te1[i] = te1[i];
    s_te2[i] = te2[i];
    s_te3[i] = te3[i];
    s_te4[i] = te4[i];
  }

  SYNC_THREADS ();

  #else

  CONSTANT_AS u32a *s_te0 = te0;
  CONSTANT_AS u32a *s_te1 = te1;
  CONSTANT_AS u32a *s_te2 = te2;
  CONSTANT_AS u32a *s_te3 = te3;
  CONSTANT_AS u32a *s_te4 = te4;

  #endif

  if (gid >= GID_CNT) return;

  /**
   * CT
   */

  u32 iv[4];

  iv[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  iv[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  iv[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  iv[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  u32 ct[4];

  ct[0] = salt_bufs[SALT_POS_HOST].salt_buf[4];
  ct[1] = salt_bufs[SALT_POS_HOST].salt_buf[5];
  ct[2] = salt_bufs[SALT_POS_HOST].salt_buf[6];
  ct[3] = salt_bufs[SALT_POS_HOST].salt_buf[7];

  /**
   * digest
   */

  const u32 search[4] =
  {
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R0],
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R1],
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R2],
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R3]
  };

  /**
   * base
   */

  COPY_PW (pws[gid]);

  /**
   * loop
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos++)
  {
    pw_t tmp = PASTE_PW;

    tmp.pw_len = apply_rules (rules_buf[il_pos].cmds, tmp.i, tmp.pw_len);

    u32 ukey[8];

    sha1_hmac_ctx_t sha1_hmac_ctx;

    sha1_hmac_init_swap (&sha1_hmac_ctx, tmp.i, tmp.pw_len);

    u32 w0[4];
    u32 w1[4];
    u32 w2[4];
    u32 w3[4];

    w0[0] = iv[0];
    w0[1] = iv[1];
    w0[2] = iv[2];
    w0[3] = iv[3];
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx, w0, w1, w2, w3, 16);

    sha1_hmac_ctx_t sha1_hmac_ctx2 = sha1_hmac_ctx;

    w0[0] = 1;
    w0[1] = 0;
    w0[2] = 0;
    w0[3] = 0;
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx2, w0, w1, w2, w3, 4);

    sha1_hmac_final (&sha1_hmac_ctx2);

    ukey[0] = sha1_hmac_ctx2.opad.h[0];
    ukey[1] = sha1_hmac_ctx2.opad.h[1];
    ukey[2] = sha1_hmac_ctx2.opad.h[2];
    ukey[3] = sha1_hmac_ctx2.opad.h[3];
    ukey[4] = sha1_hmac_ctx2.opad.h[4];

    sha1_hmac_ctx_t sha1_hmac_ctx3 = sha1_hmac_ctx;

    w0[0] = 2;
    w0[1] = 0;
    w0[2] = 0;
    w0[3] = 0;
    w1[0] = 0;
    w1[1] = 0;
    w1[2] = 0;
    w1[3] = 0;
    w2[0] = 0;
    w2[1] = 0;
    w2[2] = 0;
    w2[3] = 0;
    w3[0] = 0;
    w3[1] = 0;
    w3[2] = 0;
    w3[3] = 0;

    sha1_hmac_update_64 (&sha1_hmac_ctx3, w0, w1, w2, w3, 4);

    sha1_hmac_final (&sha1_hmac_ctx3);

    ukey[5] = sha1_hmac_ctx3.opad.h[0];
    ukey[6] = sha1_hmac_ctx3.opad.h[1];
    ukey[7] = sha1_hmac_ctx3.opad.h[2];

    #define KEYLEN 60

    u32 ks[KEYLEN];

    AES256_set_encrypt_key (ks, ukey, s_te0, s_te1, s_te2, s_te3);

    u32 out[4];

    AES256_encrypt (ks, iv, out, s_te0, s_te1, s_te2, s_te3, s_te4);

    u32 pt[4];

    pt[0] = ct[0] ^ out[0];
    pt[1] = ct[1] ^ out[1];
    pt[2] = ct[2] ^ out[2];
    pt[3] = ct[3] ^ out[3];

    if (is_valid_char (pt[0]) == 0) continue;
    if (is_valid_char (pt[1]) == 0) continue;
    if (is_valid_char (pt[2]) == 0) continue;
    if (is_valid_char (pt[3]) == 0) continue;

    int i;

    for (i = 8; i < 16; i += 4)
    {
      AES256_encrypt (ks, out, out, s_te0, s_te1, s_te2, s_te3, s_te4);

      pt[0] = salt_bufs[SALT_POS_HOST].salt_buf[i + 0] ^ out[0];
      pt[1] = salt_bufs[SALT_POS_HOST].salt_buf[i + 1] ^ out[1];
      pt[2] = salt_bufs[SALT_POS_HOST].salt_buf[i + 2] ^ out[2];
      pt[3] = salt_bufs[SALT_POS_HOST].salt_buf[i + 3] ^ out[3];

      if (is_valid_char (pt[0]) == 0) break;
      if (is_valid_char (pt[1]) == 0) break;
      if (is_valid_char (pt[2]) == 0) break;
      if (is_valid_char (pt[3]) == 0) break;
    }

    if (i < 16) continue;

    const u32 r0 = ct[0];
    const u32 r1 = ct[1];
    const u32 r2 = ct[2];
    const u32 r3 = ct[3];

    COMPARE_S_SCALAR (r0, r1, r2, r3);
  }
}
