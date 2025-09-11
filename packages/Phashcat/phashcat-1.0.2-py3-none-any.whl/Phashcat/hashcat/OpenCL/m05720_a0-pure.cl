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
#include M2S(INCLUDE_PATH/inc_hash_sha256.cl)
#endif

KERNEL_FQ KERNEL_FA void m05720_mxx (KERN_ATTR_RULES ())
{
  /**
   * modifier
   */

  const u64 lid = get_local_id (0);
  const u64 gid = get_global_id (0);

  if (gid >= GID_CNT) return;

  /**
   * base
   */

  COPY_PW (pws[gid]);

  const u32 salt_iter = salt_bufs[SALT_POS_HOST].salt_iter;

  sha256_ctx_t ctx0;

  sha256_init (&ctx0);

  sha256_update_global (&ctx0, salt_bufs[SALT_POS_HOST].salt_buf, salt_bufs[SALT_POS_HOST].salt_len);

  /**
   * loop
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos++)
  {
    pw_t tmp = PASTE_PW;

    tmp.pw_len = apply_rules (rules_buf[il_pos].cmds, tmp.i, tmp.pw_len);

    sha256_ctx_t ctx = ctx0;

    sha256_update_swap (&ctx, tmp.i, tmp.pw_len);

    sha256_final (&ctx);

    u32 digest[8];

    digest[0] = ctx.h[0];
    digest[1] = ctx.h[1];
    digest[2] = ctx.h[2];
    digest[3] = ctx.h[3];
    digest[4] = ctx.h[4];
    digest[5] = ctx.h[5];
    digest[6] = ctx.h[6];
    digest[7] = ctx.h[7];

    // iterations

    u32 wt0[4];
    u32 wt1[4];
    u32 wt2[4];
    u32 wt3[4];

    for (u32 i = 0; i < salt_iter; i++)
    {
      wt0[0] = digest[0];
      wt0[1] = digest[1];
      wt0[2] = digest[2];
      wt0[3] = digest[3];
      wt1[0] = digest[4];
      wt1[1] = digest[5];
      wt1[2] = digest[6];
      wt1[3] = digest[7];
      wt2[0] = 0x80000000;
      wt2[1] = 0;
      wt2[2] = 0;
      wt2[3] = 0;
      wt3[0] = 0;
      wt3[1] = 0;
      wt3[2] = 0;
      wt3[3] = 32 * 8;

      digest[0] = SHA256M_A;
      digest[1] = SHA256M_B;
      digest[2] = SHA256M_C;
      digest[3] = SHA256M_D;
      digest[4] = SHA256M_E;
      digest[5] = SHA256M_F;
      digest[6] = SHA256M_G;
      digest[7] = SHA256M_H;

      sha256_transform (wt0, wt1, wt2, wt3, digest);
    }

    const u32 r0 = digest[DGST_R0];
    const u32 r1 = digest[DGST_R1];
    const u32 r2 = digest[DGST_R2];
    const u32 r3 = digest[DGST_R3];

    COMPARE_M_SCALAR (r0, r1, r2, r3);
  }
}

KERNEL_FQ KERNEL_FA void m05720_sxx (KERN_ATTR_RULES ())
{
  /**
   * modifier
   */

  const u64 lid = get_local_id (0);
  const u64 gid = get_global_id (0);

  if (gid >= GID_CNT) return;

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

  const u32 salt_iter = salt_bufs[SALT_POS_HOST].salt_iter;

  sha256_ctx_t ctx0;

  sha256_init (&ctx0);

  sha256_update_global (&ctx0, salt_bufs[SALT_POS_HOST].salt_buf, salt_bufs[SALT_POS_HOST].salt_len);

  /**
   * loop
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos++)
  {
    pw_t tmp = PASTE_PW;

    tmp.pw_len = apply_rules (rules_buf[il_pos].cmds, tmp.i, tmp.pw_len);

    sha256_ctx_t ctx = ctx0;

    sha256_update_swap (&ctx, tmp.i, tmp.pw_len);

    sha256_final (&ctx);

    u32 digest[8];

    digest[0] = ctx.h[0];
    digest[1] = ctx.h[1];
    digest[2] = ctx.h[2];
    digest[3] = ctx.h[3];
    digest[4] = ctx.h[4];
    digest[5] = ctx.h[5];
    digest[6] = ctx.h[6];
    digest[7] = ctx.h[7];

    // iterations

    u32 wt0[4];
    u32 wt1[4];
    u32 wt2[4];
    u32 wt3[4];

    for (u32 i = 0; i < salt_iter; i++)
    {
      wt0[0] = digest[0];
      wt0[1] = digest[1];
      wt0[2] = digest[2];
      wt0[3] = digest[3];
      wt1[0] = digest[4];
      wt1[1] = digest[5];
      wt1[2] = digest[6];
      wt1[3] = digest[7];
      wt2[0] = 0x80000000;
      wt2[1] = 0;
      wt2[2] = 0;
      wt2[3] = 0;
      wt3[0] = 0;
      wt3[1] = 0;
      wt3[2] = 0;
      wt3[3] = 32 * 8;

      digest[0] = SHA256M_A;
      digest[1] = SHA256M_B;
      digest[2] = SHA256M_C;
      digest[3] = SHA256M_D;
      digest[4] = SHA256M_E;
      digest[5] = SHA256M_F;
      digest[6] = SHA256M_G;
      digest[7] = SHA256M_H;

      sha256_transform (wt0, wt1, wt2, wt3, digest);
    }

    const u32 r0 = digest[DGST_R0];
    const u32 r1 = digest[DGST_R1];
    const u32 r2 = digest[DGST_R2];
    const u32 r3 = digest[DGST_R3];

    COMPARE_S_SCALAR (r0, r1, r2, r3);
  }
}
