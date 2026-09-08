#pragma once

#include "CoreMinimal.h"
#include "Engine/Texture2D.h"
#include "Widgets/SLeafWidget.h"
#include "Rendering/DrawElementTypes.h"
#include "Styling/CoreStyle.h"

/** Slow crossfades between real map captures; no live level or scene capture required. */
class SScenicMenuBackdrop : public SLeafWidget
{
public:
 SLATE_BEGIN_ARGS(SScenicMenuBackdrop) {} SLATE_END_ARGS()
 void Construct(const FArguments&, const TArray<TObjectPtr<UTexture2D>>& Textures)
 {
  for (UTexture2D* Texture : Textures)
  {
   FSlateBrush Brush;
   Brush.SetResourceObject(Texture);
   Brush.ImageSize=FVector2D(Texture->GetSizeX(),Texture->GetSizeY());
   Brush.DrawAs=ESlateBrushDrawType::Image;
   Brushes.Add(Brush);
  }
  StartedAt=FPlatformTime::Seconds();
  SetCanTick(true);
  SetVisibility(EVisibility::HitTestInvisible);
 }
 virtual void Tick(const FGeometry&,double,float) override { Invalidate(EInvalidateWidgetReason::Paint); }
 virtual FVector2D ComputeDesiredSize(float) const override { return FVector2D(1920,1080); }
 virtual int32 OnPaint(const FPaintArgs&,const FGeometry& Geometry,const FSlateRect&,
  FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle&,bool) const override
 {
  const FVector2D Size=Geometry.GetLocalSize();
  if (Brushes.IsEmpty() || Size.X<=0 || Size.Y<=0) return Layer;
  const double Time=FPlatformTime::Seconds()-StartedAt;
  const int32 Current=static_cast<int32>(Time/12.0)%Brushes.Num();
  const float Fade=FMath::SmoothStep(10.f,12.f,static_cast<float>(FMath::Fmod(Time,12.0)));
  auto PaintCapture=[&](int32 Index,float Alpha,int32 AtLayer)
  {
   FSlateBrush Brush=Brushes[Index];
   // Existing captures include a flashlight on the right. Select the scenic left
   // 66% before aspect-fill cropping, preserving proportions at any window size.
   const FVector2D ImageSize=Brush.ImageSize;
   FVector2D Extent(.66,1.0);
   const double SourceAspect=ImageSize.X*Extent.X/(ImageSize.Y*Extent.Y);
   const double TargetAspect=Size.X/Size.Y;
   if (SourceAspect>TargetAspect) Extent.X*=TargetAspect/SourceAspect;
   else Extent.Y*=SourceAspect/TargetAspect;
   const FVector2D Center(.33,.5);
   Brush.SetUVRegion(FBox2d(Center-Extent*.5,Center+Extent*.5));
   FSlateDrawElement::MakeBox(Out,AtLayer,Geometry.ToPaintGeometry(),&Brush,
    ESlateDrawEffect::None,FLinearColor(1,1,1,Alpha));
  };
  PaintCapture(Current,1,Layer);
  if (Fade>0) PaintCapture((Current+1)%Brushes.Num(),Fade,Layer+1);
  FSlateDrawElement::MakeBox(Out,Layer+2,Geometry.ToPaintGeometry(),FCoreStyle::Get().GetBrush("WhiteBrush"),
   ESlateDrawEffect::None,FLinearColor(0,0,0,.24f));
  return Layer+2;
 }
private:
 TArray<FSlateBrush> Brushes;
 double StartedAt=0;
};
